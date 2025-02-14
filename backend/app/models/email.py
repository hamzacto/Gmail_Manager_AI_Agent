from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class EmailBase(BaseModel):
    subject: str
    body: str
    to: List[EmailStr]
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None

class EmailCreate(BaseModel):
    recipients: List[str]
    subject: str
    body: str

class EmailResponse(BaseModel):
    id: str
    threadId: str
    sender: EmailStr
    date: datetime
    priority: str
    
    class Config:
        from_attributes = True

class DraftRequest(BaseModel):
    context: str
    recipient: Optional[EmailStr] = None

class CommandRequest(BaseModel):
    command: str 