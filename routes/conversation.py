from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from AI.aiManager import gerarRespostaStream

from AI.Modelos import Modelos
from AI.Personas import Personas
from database.chats import *

import json

from pydantic import BaseModel

router = APIRouter(
    prefix="/conversation",
    tags=["conversation"],
)

class ConversationUpdate(BaseModel):
    title: str

class ConversationCreate(BaseModel):
    title: str
    description: str

class MessageRequest(BaseModel):
    user_input: str
    model: Modelos = Modelos.DeepSeek
    persona: Personas = Personas.Roteirista

def gerarResposta(id: str, prompt : str, modelo : Modelos = Modelos.DeepSeek, persona : Personas = Personas.Roteirista):
    userPrompt = {"role": "user", "content": prompt}

    historico = getChatHistory(id)["messages"]

    historico.append(userPrompt)

    addMessage(id, userPrompt)

    resposta = {
        "role": "assistant",
        "content": "",
        "reasoning": "",
    }
    
    for response in gerarRespostaStream(historico, modelo):
        resposta["content"] = resposta["content"] + response["content"]
        resposta["reasoning"] = resposta["reasoning"] + response["reasoning"]

        yield json.dumps(response) + "\n"

    addMessage(id, resposta)

    return []

@router.get("/history/{conversation_id}",)
async def get_conversation_history(conversation_id: str):
   resultado = getChatHistory(conversation_id)

   if(resultado == None):
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")

   return resultado["messages"]

@router.get("/{conversation_id}",)
async def get_conversation_history(conversation_id: str):
   resultado = getChat(conversation_id)

   if(resultado == None):
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")

   return resultado

@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str):
    resultado = deleteChat(conversation_id)

    if(not resultado):
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")

    return {"message": "Chat deleted successfully."}

@router.patch("/{conversation_id}")
async def update_conversation_title(conversation_id: str, payload: ConversationUpdate):
    return updateChatTitle(conversation_id, payload.title)

@router.post("/{conversation_id}/message")
async def send_message(conversation_id: str, payload: MessageRequest):
    return StreamingResponse(gerarResposta(conversation_id, payload.user_input, modelo=payload.model, persona=payload.persona), media_type="text/event-stream")


@router.post("/", status_code=201)
async def create_conversation(payload: ConversationCreate):
    return createChat(payload.title, payload.description)
    
@router.get("/")
async def list_conversations():
    return getAllChatsDescriptions()