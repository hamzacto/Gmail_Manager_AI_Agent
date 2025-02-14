from contextlib import asynccontextmanager
from fastapi.testclient import TestClient
import pytest
import asyncio

from app.main import app
from app.services.gmail_service import GmailService
from app.services.ai_service import AIService
from app.api.deps import get_current_user

# Override the current user dependency to always return a dummy user with credentials
def fake_get_current_user():
    return {
        "id": "dummy",
        "email": "dummy@example.com",
        "credentials": {
            "client_id": "dummy_client_id",
            "client_secret": "dummy_secret",
            "refresh_token": "dummy_refresh_token",
            "token_uri": "https://oauth2.googleapis.com/token",
            "token": "dummy_token",
            "scopes": ["https://www.googleapis.com/auth/gmail.modify"]
        }
    }

app.dependency_overrides[get_current_user] = fake_get_current_user

# Mock Gmail API service methods
class MockGmailService:
    async def get_recent_emails(self, limit=10):
        return [
            {
                "id": str(i),
                "subject": f"Test Email {i}",
                "snippet": f"Snippet for email {i}",
                "date": "2024-03-20",
                "sender": "test@example.com",
            }
            for i in range(1, limit + 1)
        ]

    async def send_email(self, to, subject, body):
        return {"id": "dummy_message_id"}

# Override GmailService initialization
def mock_gmail_service_init(self, user_credentials):
    pass

GmailService.__init__ = mock_gmail_service_init
GmailService.get_recent_emails = MockGmailService.get_recent_emails
GmailService.send_email = MockGmailService.send_email

# Mock AI service
class MockAIService:
    async def interpret_command(self, command, gmail_service):
        return {"output": f"Processed command: {command}"}

    async def ainvoke(self, context):
        return {"dummy": "value"}

def mock_ai_service_init(self, *args, **kwargs):
    self.llm = MockAIService()

AIService.__init__ = mock_ai_service_init
AIService.interpret_command = MockAIService.interpret_command

# Add health endpoint to the app
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "groq_api": "connected",
        "version": "1.0.0"
    }

# Disable lifespan events so that failing startup events (like ChatGroq initialization) do not affect tests.
@asynccontextmanager
async def empty_lifespan(app):
    yield

app.router.lifespan_context = empty_lifespan

client = TestClient(app)

def test_get_recent_emails():
    # Test GET /api/v1/emails/recent
    response = client.get("/api/v1/emails/recent?limit=3")
    assert response.status_code == 200
    emails = response.json()
    assert isinstance(emails, list)
    assert len(emails) == 3
    email = emails[0]
    assert "id" in email
    assert "subject" in email
    assert "snippet" in email
    assert "date" in email
    assert "sender" in email

def test_process_command():
    # Test POST /api/emails/process-command
    payload = {"command": "test command"}
    response = client.post("/api/emails/process-command", json=payload)
    assert response.status_code == 200
    # The expected output should match the dummy implementation.
    assert response.json() == "Processed command: test command" 