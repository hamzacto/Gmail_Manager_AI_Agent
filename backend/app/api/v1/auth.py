from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from ...core.config import settings
from ...core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/google/url")
async def get_authorization_url():
    """Get the Google OAuth2 authorization URL"""
    try:
        flow = Flow.from_client_secrets_file(
            settings.CLIENT_SECRETS_FILE,
            scopes=settings.GOOGLE_SCOPES
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return {"url": authorization_url}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/callback")
async def auth_callback(code: str, state: str):
    """Handle the Google OAuth2 callback"""
    try:
        flow = Flow.from_client_secrets_file(
            settings.CLIENT_SECRETS_FILE,
            scopes=settings.GOOGLE_SCOPES,
            state=state
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Get user email from Gmail API
        service = build("gmail", "v1", credentials=credentials)
        profile = service.users().getProfile(userId="me").execute()
        email = profile.get("emailAddress")
        
        # Create JWT token with additional user info
        token_data = {
            "sub": email,
            "email": email,
            "credentials": {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes
            }
        }
        
        access_token = create_access_token(data=token_data)
        
        return HTMLResponse(content=f"""
            <html>
                <script>
                    window.opener.postMessage({{
                        token: "{access_token}",
                        type: "bearer",
                        status: "gmail_connected"
                    }}, "*");
                    window.close();
                </script>
                <body>
                    <h2>Authentification réussie !</h2>
                    <p>Vous pouvez fermer cette fenêtre.</p>
                </body>
            </html>
        """)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        ) 