
import os
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agents import Runner, Agent
from agents.memory.session import SessionABC
from agents.items import TResponseInputItem

from ai_config import config
from custom_agents import test_agent

CONVERSATION_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = timedelta(minutes=30)

async def cleanup_expired_conversations():
    """A background task to periodically remove expired conversations from the cache."""
    while True:
        
        expired_ids = []
        for conv_id, cache_entry in CONVERSATION_CACHE.items():
            if datetime.now() - cache_entry["timestamp"] > CACHE_TTL:
                expired_ids.append(conv_id)
        
        for conv_id in expired_ids:
            
            if conv_id in CONVERSATION_CACHE:
                del CONVERSATION_CACHE[conv_id]
                print(f"Cleaned up expired conversation: {conv_id}")

        
        await asyncio.sleep(300)

app = FastAPI()
load_dotenv()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_expired_conversations())

origins = os.environ.get("FRONTEND_URLS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConversationCreate(BaseModel):
    title: str
    description: str

class MessageRequest(BaseModel):
    user_input: str

class CustomSession(SessionABC):
    """
    Refactored session implementation to use the global in-memory cache
    instead of the file system.
    """
    def __init__(self, session_id: str):
        self.session_id = session_id

    def _get_session_data(self) -> Dict[str, Any] | None:
        """Helper to retrieve non-expired session data from the cache."""
        cache_entry = CONVERSATION_CACHE.get(self.session_id)
        if not cache_entry:
            return None
        
        if datetime.now() - cache_entry["timestamp"] > CACHE_TTL:
            del CONVERSATION_CACHE[self.session_id] 
            return None
        return cache_entry.get("data")

    def _update_session_data(self, data: Dict[str, Any]):
        """Helper to update session data and its timestamp in the cache."""
        CONVERSATION_CACHE[self.session_id] = {
            "data": data,
            "timestamp": datetime.now() 
        }

    async def get_items(self, limit: int | None = None) -> List[TResponseInputItem]:
        session_data = self._get_session_data()
        if not session_data:
            return []
        
        conv = session_data.get("conversation", [])
        return conv[-limit:] if limit is not None else conv

    async def add_items(self, items: List[TResponseInputItem]) -> None:
        session_data = self._get_session_data()
        if session_data is None:
            
            raise HTTPException(status_code=404, detail="Conversation not found or has expired")
        
        session_data["conversation"].extend(items)
        self._update_session_data(session_data)

    async def pop_item(self) -> TResponseInputItem | None:
        session_data = self._get_session_data()
        if not session_data or not session_data.get("conversation"):
            return None
        
        item = session_data["conversation"].pop()
        self._update_session_data(session_data)
        return item

    async def clear_session(self) -> None:
        session_data = self._get_session_data()
        if session_data:
            session_data["conversation"] = []
            self._update_session_data(session_data)

def extract_text(item: Dict[str, Any]) -> Dict[str, str] | None:
    if item.get("role") == "user":
        return item
    elif item.get("status") == "completed":
        message = item.get("content", [{}])[0].get("text", "")
        return {"content": message, "role": "assistant"}
    return None

@app.post("/message/{conversation_id}")
async def send_message(conversation_id: str, payload: MessageRequest):
    if conversation_id not in CONVERSATION_CACHE:
        raise HTTPException(status_code=404, detail="Conversation not found or has expired")
    
    session = CustomSession(conversation_id)
    
    result = await Runner.run(test_agent, payload.user_input, run_config=config, session=session)
    return {"content": result.final_output, "role": "assistant"}

@app.get("/conversation/history/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    session = CustomSession(conversation_id)
    conversation_content = await session.get_items()

    if not conversation_content and conversation_id not in CONVERSATION_CACHE:
        raise HTTPException(status_code=404, detail="Conversation not found or has expired")
        
    
    conversation = [msg for item in conversation_content if (msg := extract_text(item)) is not None]
    return conversation

@app.delete("/conversation/{conversation_id}")
async def delete_conversation_history(conversation_id: str):
    if conversation_id in CONVERSATION_CACHE:
        del CONVERSATION_CACHE[conversation_id]
        return {"status": "ok", "message": "Conversation deleted."}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.post("/conversation")
async def create_conversation(payload: ConversationCreate):
    
    conversation_id = str(uuid.uuid4())
    
    session_data = {
        "session_id": conversation_id,
        "title": payload.title,
        "description": payload.description,
        "conversation": []
    }
    
    CONVERSATION_CACHE[conversation_id] = {
        "data": session_data,
        "timestamp": datetime.now()
    }
    
    return {
        "id": conversation_id,
        "title": payload.title,
        "description": payload.description
    }
    
@app.get("/conversation")
async def list_conversations():
    conversations_list = []
    
    for conv_id, cache_entry in list(CONVERSATION_CACHE.items()):
        
        if datetime.now() - cache_entry["timestamp"] <= CACHE_TTL:
            data = cache_entry["data"]
            conversations_list.append({
                "id": data["session_id"],
                "title": data["title"],
                "description": data["description"]
            })
    return conversations_list