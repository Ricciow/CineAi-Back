from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
from agents import Runner
import json
from ai_config import config
from custom_agents import *
from custom_session import CustomSession
from models import ConversationBase, ConversationCreate, MessageRequest

app = FastAPI()

#Extrai apenas as mensagens e os "roles"
def extract_text(item):
    if item["role"] == "user":
        return item
    elif item["status"] == "completed":
        message = item.get("content")[0]["text"]
        return {"content":message, "role":"assistant"}
    return None

@app.post("/message")
async def send_message(payload: MessageRequest):
    session = CustomSession(payload.conversation_id)
    result = await Runner.run(test_agent, payload.user_input, run_config = config, session = session)
    content = {"content": result.final_output, "role": "assistant"}
    return content

@app.get("/conversation-history")
async def get_conversation_history(payload: ConversationBase):
    session = CustomSession(payload.conversation_id)
    conversation_content = await session.get_items()
    conversation = []
    for item in conversation_content:
        message = extract_text(item)
        conversation.append(message)
    return conversation

@app.delete("/conversation-history")
async def delete_conversation_history(payload: ConversationBase):
    try:
        os.remove("./conversations/"+payload.conversation_id+".json")
        return "200"
    except FileNotFoundError:
        return "File not found"

@app.post("/conversation")
async def create_conversation(payload: ConversationCreate):
    session = CustomSession(payload.conversation_id, payload.title, payload.description)
    await session.clear_session()
    
