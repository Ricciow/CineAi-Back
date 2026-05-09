from pydantic import BaseModel, EmailStr
from typing import List, Optional

class ProjectPermissions(BaseModel):
    send_messages: bool = True
    read: bool = True
    create_chats: bool = True
    image: bool = False
    video: bool = False

class ProjectMember(BaseModel):
    user_id: str
    email: str
    role: str  # "admin" or "member"
    permissions: ProjectPermissions

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: str
    user_id: str
    members: List[ProjectMember] = []

class MemberAddRequest(BaseModel):
    email: EmailStr
    role: str = "member"
    permissions: Optional[ProjectPermissions] = None

class MemberUpdateRequest(BaseModel):
    role: Optional[str] = None
    permissions: Optional[ProjectPermissions] = None

class TransferOwnershipRequest(BaseModel):
    new_owner_email: EmailStr
