from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from .core.config import Settings, settings
from .services.gmail_service import GmailService
from .services.ai_service import AIService
from .api.deps import get_current_user
from typing import Dict
from .api.v1 import auth, emails
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel

app = FastAPI(title=settings.PROJECT_NAME)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(emails.router, prefix=settings.API_V1_STR)

class CommandRequest(BaseModel):
    command: str

# Email routes
@app.get(f"{settings.API_V1_STR}/emails/recent")
async def get_recent_emails(
    limit: int = 10,
    current_user = Depends(get_current_user)
):
    gmail_service = GmailService(current_user)
    emails = await gmail_service.get_recent_emails(limit)
    return emails

@app.post("/api/emails/process-command")
async def process_command(
    command_req: CommandRequest = Body(...),
    current_user = Depends(get_current_user)
):
    try:
        ai_service = AIService()
        gmail_service = GmailService(current_user)
        
        # Process natural language command
        result = await ai_service.interpret_command(command_req.command, gmail_service)
        return result["output"]
            
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Check the health of the system components.
    Returns:
        Dict with status of each component and overall health
    """
    try:
        # Initialize services to check their configuration
        ai_service = AIService()
        
        # Test Groq API connection using ChatPromptTemplate
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a test assistant"),
            ("user", "test")
        ])
        chain = prompt | ai_service.llm
        await chain.ainvoke({"context": "test"})
        
        return {
            "status": "healthy",
            "groq_api": "connected",
            "version": settings.VERSION
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "version": settings.VERSION
            }
        )
@app.get("/health_check")
async def health():
    return {"status": "ok"}