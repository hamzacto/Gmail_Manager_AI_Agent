from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional
from ...models.email import EmailResponse, EmailCreate, DraftRequest
from ...services.gmail_service import GmailService
from ...services.ai_service import AIService
from ..deps import get_current_user
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime

router = APIRouter(prefix="/emails", tags=["emails"])

class EmailCreate(BaseModel):
    recipients: List[EmailStr]
    subject: constr(min_length=1, strip_whitespace=True)
    body: constr(min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "recipients": ["recipient@example.com"],
                "subject": "Meeting Tomorrow",
                "body": "Hello, let's meet tomorrow at 10 AM."
            }
        }

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
    if not email.recipients:
        raise HTTPException(
            status_code=422,
            detail="At least one recipient is required"
        )
    
    gmail_service = GmailService(current_user)
    try:
        result = await gmail_service.send_email(
            to=email.recipients[0],
            subject=email.subject,
            body=email.body
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        ) 