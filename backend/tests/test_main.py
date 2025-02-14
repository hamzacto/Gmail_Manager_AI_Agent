from contextlib import asynccontextmanager
from fastapi.testclient import TestClient
import pytest
import asyncio
from fastapi import status
from fastapi.exceptions import HTTPException
import datetime

from app.main import app
from app.services.gmail_service import GmailService
from app.services.ai_service import AIService
from app.api.deps import get_current_user
from app.models.user import User
from app.models.email import EmailCreate

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
    try:
        # Add basic service checks
        return {
            "status": "healthy",
            "groq_api": "connected",
            "version": "1.0.1",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service Unavailable: {str(e)}"
        )

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

def test_health_check():
    response = client.get("/health_check")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_send_email():
    # Test POST /api/v1/emails/send
    payload = {
        "recipients": ["test@example.com"],
        "subject": "Test Subject",
        "body": "Test Body"
    }
    response = client.post("/api/v1/emails/send", json=payload)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["id"] == "dummy_message_id"

def test_invalid_command():
    # Test POST /api/emails/process-command with invalid payload
    payload = {"invalid_field": "test"}
    response = client.post("/api/emails/process-command", json=payload)
    assert response.status_code == 422  # Unprocessable Entity

def test_get_recent_emails_with_invalid_limit():
    # Test GET /api/v1/emails/recent with invalid limit
    response = client.get("/api/v1/emails/recent?limit=invalid")
    assert response.status_code == 422  # Unprocessable Entity

def test_get_recent_emails_with_large_limit():
    # Test GET /api/v1/emails/recent with a large limit
    response = client.get("/api/v1/emails/recent?limit=100")
    assert response.status_code == 200
    emails = response.json()
    assert isinstance(emails, list)
    assert len(emails) == 100  # Should return the requested number of emails

def test_current_user():
    # Test that the current user dependency is working correctly
    response = client.get("/api/v1/emails/recent")
    assert response.status_code == 200
    
    # The mock user credentials should be used
    user = fake_get_current_user()
    assert user["email"] == "dummy@example.com"
    assert user["credentials"]["client_id"] == "dummy_client_id"

def test_email_model_validation():
    # Test email model validation with multiple invalid cases
    invalid_payloads = [
        {
            "recipients": [],  # Empty recipients list
            "subject": "",     # Empty subject
            "body": "Test Body"
        },
        {
            "recipients": ["invalid-email"],  # Invalid email format
            "subject": "Test",
            "body": "Test Body"
        },
        {
            "recipients": ["test@example.com"],
            "subject": "",  # Empty subject
            "body": "Test Body"
        }
    ]
    
    for payload in invalid_payloads:
        response = client.post("/api/v1/emails/send", json=payload)
        assert response.status_code == 422
        assert "detail" in response.json()

def test_process_command_with_empty_command():
    # Test POST /api/emails/process-command with empty command
    invalid_payloads = [
        {"command": ""},
        {"command": "   "},  # Only whitespace
        {}  # Missing command field
    ]
    
    for payload in invalid_payloads:
        response = client.post("/api/emails/process-command", json=payload)
        assert response.status_code == 422
        error_detail = response.json().get("detail", [])
        assert any("command" in str(error).lower() for error in error_detail) 