from pydantic import BaseModel

class ConversationBase(BaseModel):
    conversation_id: str 
    title: str | None = None
    description: str | None = None


class ConversationCreate(ConversationBase):
    title: str
    description: str

class MessageRequest(BaseModel):
    user_input: str