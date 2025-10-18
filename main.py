from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from agents import Runner
import json
from ai_config import config
from custom_agents import *
from custom_session import CustomSession
from models import ConversationBase, ConversationCreate, MessageRequest

app = FastAPI()
load_dotenv()
origins = os.environ.get("FRONTEND_URLS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Permite as origens da lista
    allow_credentials=True,
    allow_methods=["*"],         # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],         # Permite todos os cabeçalhos
)


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
    if conversation != []:
        return conversation
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.delete("/conversation-history")
async def delete_conversation_history(payload: ConversationBase):
    try:
        os.remove("./conversations/"+payload.conversation_id+".json")
        return "200"
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.post("/conversation")
async def create_conversation(payload: ConversationCreate):
    session = CustomSession(payload.conversation_id, payload.title, payload.description)
    await session.clear_session()
    
@app.get("/all-conversations")
async def list_conversations():
    path = "./conversations"
    conversation_files = os.listdir(path)
    conversations_list = []
    for i in conversation_files:
        with open(path+"/"+i, "r", encoding="utf-8") as f:
            data = json.load(f)
        conversations_list.append({"session_id":data["session_id"], "title":data["title"],"description":data["description"] })
    if conversations_list == []:
        raise HTTPException(status_code=404, detail="No conversations found")
    return conversations_list