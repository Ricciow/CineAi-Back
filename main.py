from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, SQLiteSession
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
    session = CustomSession(payload.conversation_id)
    await session.clear_session()
    
