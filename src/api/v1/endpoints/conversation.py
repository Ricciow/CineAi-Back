import json
import logging
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
logger = logging.getLogger(__name__)

async def generate_response_and_store(
    chat_id: str, 
    prompt: str, 
    user_id: str,
    model: AIModel, 
    persona: AIPersona
):
    try:
        user_message = {"role": "user", "content": prompt}
        history = chat_repository.get_history(chat_id) or []

        chat_repository.add_message(chat_id, user_message)

        full_history = history + [user_message]

        assistant_response = {
            "role": "assistant",
            "content": "",
            "reasoning": "",
        }

        async for chunk in ai_service.generate_response_stream(full_history, model, persona):
            assistant_response["content"] += chunk.get("content", "")
            assistant_response["reasoning"] += chunk.get("reasoning", "")
            yield json.dumps(chunk) + "\n"

        if assistant_response["content"] or assistant_response["reasoning"]:
            chat_repository.add_message(chat_id, assistant_response)
            
            if len(history) == 0:
                new_description = await ai_service.generate_description(
                    prompt, assistant_response["content"]
                )
                chat_repository.update_description(chat_id, new_description)
                yield json.dumps({"description": new_description}) + "\n"
            
    except Exception as e:
        logger.error(f"Error in generate_response_and_store: {e}")
        error_msg = {"role": "assistant", "content": f"\n\n[Erro: {str(e)}]", "reasoning": ""}
        yield json.dumps(error_msg) + "\n"

async def check_chat_permission(chat_id: str, user_id: str, permission: str):
    chat = chat_repository.get_by_id(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    if chat.get("project_id"):
        from src.repositories.project_repository import project_repository
        project = project_repository.get_by_id(chat["project_id"])
        if not project:
             raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        is_owner = project["user_id"] == user_id
        member = next((m for m in project.get("members", []) if m["user_id"] == user_id), None)
        
        if not is_owner and not member:
            raise HTTPException(status_code=403, detail="Sem acesso a este projeto")
        
        if is_owner or member["role"] == "admin":
            return chat
            
        if not member["permissions"].get(permission, False):
            raise HTTPException(status_code=403, detail=f"Você não tem permissão para: {permission}")
    else:
        if chat["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Sem acesso a esta conversa")
            
    return chat

@router.get("/history/{conversation_id}")
async def get_conversation_history(
    conversation_id: str, 
    user_id: str = Depends(get_current_user_id)
):
    await check_chat_permission(conversation_id, user_id, "read")
    history = chat_repository.get_history(conversation_id)
    return history

@router.get("/models")
async def list_models():
    return [model.info for model in AIModel]

@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str, 
    user_id: str = Depends(get_current_user_id)
):
    return await check_chat_permission(conversation_id, user_id, "read")

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str, 
    user_id: str = Depends(get_current_user_id)
):
    chat = chat_repository.get_by_id(conversation_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    can_delete = chat["user_id"] == user_id
    if chat.get("project_id"):
        from src.repositories.project_repository import project_repository
        project = project_repository.get_by_id(chat["project_id"])
        if project and (project["user_id"] == user_id or any(m["user_id"] == user_id and m["role"] == "admin" for m in project.get("members", []))):
            can_delete = True
            
    if not can_delete:
        raise HTTPException(status_code=403, detail="Sem permissão para deletar")
        
    chat_repository.delete(conversation_id)
    return None

@router.patch("/{conversation_id}")
async def update_conversation_title(
    conversation_id: str, 
    payload: ConversationUpdate, 
    user_id: str = Depends(get_current_user_id)
):
    await check_chat_permission(conversation_id, user_id, "read")
    success = chat_repository.update_title(conversation_id, payload.title)
    return {"detail": "Título atualizado com sucesso"}

@router.post("/{conversation_id}/message")
async def send_message(
    conversation_id: str, 
    payload: MessageRequest, 
    user_id: str = Depends(get_current_user_id)
):
    await check_chat_permission(conversation_id, user_id, "send_messages")

    return StreamingResponse(
        generate_response_and_store(
            conversation_id, 
            payload.user_input, 
            user_id,
            model=payload.model or AIModel.GEMINI_3_FLASH, 
            persona=payload.persona or AIPersona.ROTEIRISTA
        ), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate, 
    user_id: str = Depends(get_current_user_id)
):
    if payload.project_id:
        from src.repositories.project_repository import project_repository
        project = project_repository.get_by_id(payload.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
            
        is_owner = project["user_id"] == user_id
        member = next((m for m in project.get("members", []) if m["user_id"] == user_id), None)
        
        if not is_owner and (not member or (member["role"] == "member" and not member["permissions"].get("create_chats"))):
            raise HTTPException(status_code=403, detail="Sem permissão para criar chats neste projeto")

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
    if project_id:
        from src.repositories.project_repository import project_repository
        project = project_repository.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        is_owner = project["user_id"] == user_id
        is_member = any(m["user_id"] == user_id for m in project.get("members", []))
        
        if not is_owner and not is_member:
             raise HTTPException(status_code=403, detail="Sem acesso ao projeto")

    return chat_repository.list_by_user(user_id, project_id)
