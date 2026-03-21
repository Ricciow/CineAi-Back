from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class ClickTrack(BaseModel):
    elementId: str
    variant: str
    email: Optional[str] = None
    timestamp: Optional[datetime] = None
