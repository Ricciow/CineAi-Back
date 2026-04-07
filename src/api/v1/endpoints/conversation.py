import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from src.schemas.chat import (
    ConversationUpdate, 
    ConversationCreate, 
    MessageRequest
)
from src.repositories.chat_repository import chat_repository
from src.services.ai_service import ai_service
from src.api.deps import get_current_user_id
from src.models.ai import AIModel, AIPersona

router = APIRouter()

async def generate_response_and_store(
    chat_id: str, 
    prompt: str, 
    model: AIModel, 
    persona: AIPersona
):
    user_message = {"role": "user", "content": prompt}
    history = chat_repository.get_history(chat_id) or []
    
    # Store user message
    chat_repository.add_message(chat_id, user_message)
    
    full_history = history + [user_message]
    
    assistant_response = {
        "role": "assistant",
        "content": "",
        "reasoning": "",
    }
    
    for chunk in ai_service.generate_response_stream(full_history, model, persona):
        assistant_response["content"] += chunk["content"]
        assistant_response["reasoning"] += chunk["reasoning"]
        yield json.dumps(chunk) + "\n"

    # Store full assistant response
    chat_repository.add_message(chat_id, assistant_response)

@router.get("/history/{conversation_id}")
async def get_conversation_history(
    conversation_id: str, 
    user_id: str = Depends(get_current_user_id)
):
    history = chat_repository.get_history(conversation_id, user_id)
    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversa não encontrada."
        )
    return history

@router.get("/models")
async def list_models():
    return [model.info for model in AIModel]

@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str, 
    user_id: str = Depends(get_current_user_id)
):
    chat = chat_repository.get_by_id(conversation_id, user_id)
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversa não encontrada."
        )
    return chat

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str, 
    user_id: str = Depends(get_current_user_id)
):
    success = chat_repository.delete(conversation_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversa não encontrada."
        )
    return None

@router.patch("/{conversation_id}")
async def update_conversation_title(
    conversation_id: str, 
    payload: ConversationUpdate, 
    user_id: str = Depends(get_current_user_id)
):
    success = chat_repository.update_title(conversation_id, payload.title, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversa não encontrada."
        )
    return {"detail": "Título atualizado com sucesso"}

@router.post("/{conversation_id}/message")
async def send_message(
    conversation_id: str, 
    payload: MessageRequest, 
    user_id: str = Depends(get_current_user_id)
):
    # Verify ownership
    chat = chat_repository.get_by_id(conversation_id, user_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversa não encontrada."
        )

    return StreamingResponse(
        generate_response_and_store(
            conversation_id, 
            payload.user_input, 
            model=payload.model, 
            persona=payload.persona
        ), 
        media_type="text/event-stream"
    )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate, 
    user_id: str = Depends(get_current_user_id)
):
    return chat_repository.create(
        title=payload.title, 
        description=payload.description, 
        user_id=user_id,
        project_id=payload.project_id
    )
    
@router.get("/")
async def list_conversations(
    project_id: Optional[str] = None,
    user_id: str = Depends(get_current_user_id)
):
    return chat_repository.list_by_user(user_id, project_id)
