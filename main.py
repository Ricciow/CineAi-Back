from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, SQLiteSession
import json
from ai_config import config
from custom_agents import *


app = FastAPI()

#Extrai apenas as mensagens e os "roles"
def extract_text(item):
    if item["role"] == "user":
        return item
    elif item["status"] == "completed":
        message = item.get("content")[0]["text"]
        return {"content":message, "role":"assistant"}
    return None

@app.post("/conversation")
async def send_message(conversation_id:str, user_input:str):
    session = SQLiteSession(conversation_id, "conversations.db")
    result = await Runner.run(test_agent, user_input, run_config = config, session = session)
    return result.final_output

@app.get("/conversation-history")
async def get_conversation_history(conversation_id:str):
    session = SQLiteSession(conversation_id, "conversations.db")
    conversation_content = await session.get_items()
    conversation = []
    for item in conversation_content:
        message = extract_text(item)
        conversation.append(message)
    return conversation
