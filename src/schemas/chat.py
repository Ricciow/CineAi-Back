from pydantic import BaseModel
from typing import List, Optional
from src.models.ai import AIModel, AIPersona

class ConversationUpdate(BaseModel):
    title: str

class ConversationCreate(BaseModel):
    title: str
    description: str

class MessageRequest(BaseModel):
    user_input: str
    model: AIModel = AIModel.GEMINI_2_5_FLASH
    persona: AIPersona = AIPersona.ROTEIRISTA

class Message(BaseModel):
    role: str
    content: str
    reasoning: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    title: str
    description: str
    messages: List[Message]
