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

@app.post("/message/{conversation_id}")
async def send_message(conversation_id: str, payload: MessageRequest):
    session = CustomSession(conversation_id)
    result = await Runner.run(test_agent, payload.user_input, run_config = config, session = session)
    content = {"content": result.final_output, "role": "assistant"}
    return content

@app.get("/conversation/history/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    session = CustomSession(conversation_id)
    conversation_content = await session.get_items()
    conversation = []
    for item in conversation_content:
        message = extract_text(item)
        conversation.append(message)
    if conversation != []:
        return conversation
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.delete("/conversation/{conversation_id}")
async def delete_conversation_history(conversation_id: str):
    try:
        os.remove("./conversations/"+conversation_id+".json")
        return "200"
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.post("/conversation/{conversation_id}")
async def create_conversation(conversation_id: str, payload: ConversationCreate):
    session = CustomSession(conversation_id, payload.title, payload.description)
    await session.clear_session()
    
@app.get("/conversation")
async def list_conversations():
    path = "./conversations"
    conversation_files = os.listdir(path)
    conversations_list = []
    for i in conversation_files:
        with open(path+"/"+i, "r", encoding="utf-8") as f:
            data = json.load(f)
        conversations_list.append({"id":data["session_id"], "title":data["title"],"description":data["description"] })
    if conversations_list == []:
        raise HTTPException(status_code=404, detail="No conversations found")
    return conversations_list