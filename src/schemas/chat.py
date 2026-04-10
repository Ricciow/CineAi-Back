from pydantic import BaseModel
from typing import List, Optional
from src.models.ai import AIModel, AIPersona

class ConversationUpdate(BaseModel):
    title: str

class ConversationCreate(BaseModel):
    title: str
    description: str
    project_id: Optional[str] = None

class MessageRequest(BaseModel):
    user_input: str
    model: Optional[AIModel] = AIModel.GEMINI_3_FLASH
    persona: Optional[AIPersona] = AIPersona.ROTEIRISTA

class Message(BaseModel):
    role: str
    content: str
    reasoning: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    title: str
    description: str
    messages: List[Message]
