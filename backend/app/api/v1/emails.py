from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from ...models.email import EmailResponse, EmailCreate, DraftRequest
from ...services.gmail_service import GmailService
from ...services.ai_service import AIService
from ..deps import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/emails", tags=["emails"])

class EmailCreate(BaseModel):
    recipients: List[str]
    subject: str
    body: str

class EmailResponse(BaseModel):
    id: str
    subject: str
    sender: str
    body: str
    date: str
    priority: Optional[str] = None

class DraftRequest(BaseModel):
    context: str
    recipient: Optional[str] = None

@router.get("/recent")
async def get_recent_emails(
    limit: int = 10,
    current_user = Depends(get_current_user)
):
    gmail_service = GmailService(current_user)
    emails = await gmail_service.get_recent_emails(limit)
    return emails

@router.post("/draft")
async def create_draft(
    request: DraftRequest,
    current_user = Depends(get_current_user)
):
    ai_service = AIService()
    gmail_service = GmailService(current_user)
    
    draft = await ai_service.generate_draft(
        request.context,
        request.recipient
    )
    
    return draft

@router.post("/send")
async def send_email(
    email: EmailCreate,
    current_user = Depends(get_current_user)
):
    gmail_service = GmailService(current_user)
    
    # Send to first recipient for now (can be enhanced to support multiple recipients)
    result = await gmail_service.send_email(
        to=email.recipients[0],  # Using first recipient
        subject=email.subject,
        body=email.body
    )
    
    return result 