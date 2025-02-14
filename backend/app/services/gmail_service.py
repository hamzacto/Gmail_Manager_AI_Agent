import os
import html
from typing import List, Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from loguru import logger

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailService:
    def __init__(self, user_credentials: Dict):
        credentials_info = user_credentials.get('credentials', {})
        required_fields = ['client_id', 'client_secret', 'refresh_token', 'token_uri', 'token', 'scopes']
        if not all(field in credentials_info for field in required_fields):
            raise ValueError("Missing required credentials fields")
        self.credentials = Credentials(
            token=credentials_info.get('token'),
            refresh_token=credentials_info.get('refresh_token'),
            token_uri=credentials_info.get('token_uri'),
            client_id=credentials_info.get('client_id'),
            client_secret=credentials_info.get('client_secret'),
            scopes=credentials_info.get('scopes')
        )
        self.service = build('gmail', 'v1', credentials=self.credentials)

    async def get_recent_emails(self, limit: int = 10) -> List[Dict]:
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=limit,
                labelIds=['INBOX']
            ).execute()
            messages = results.get("messages", [])
            emails = []
            for message in messages:
                msg_data = self.service.users().messages().get(
                    userId='me', id=message['id'], format="full"
                ).execute()
                snippet = msg_data.get("snippet", "No preview available")
                headers = msg_data.get("payload", {}).get("headers", [])
                subject = next(
                    (header.get("value", "No Subject") for header in headers if header.get("name", "").lower() == "subject"),
                    "No Subject"
                )
                sender = next(
                    (header.get("value", "Unknown") for header in headers if header.get("name", "").lower() == "from"),
                    "Unknown"
                )
                date = next(
                    (header.get("value", "") for header in headers if header.get("name", "").lower() == "date"),
                    ""
                )
                emails.append({
                    "snippet": html.unescape(snippet),
                    "subject": html.unescape(subject),
                    "sender": html.unescape(sender),
                    "date": html.unescape(date)
                })
            return emails
        except Exception as e:
            logger.error(f"Error fetching recent emails: {e}")
            raise e

    async def send_email(self, to: str, subject: str, body: str) -> Dict:
        message = self._create_message(to, subject, body)
        sent_message = self.service.users().messages().send(
            userId="me", body=message
        ).execute()
        return sent_message

    def _create_message(self, to: str, subject: str, body: str) -> Dict:
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        import base64

        mime_message = MIMEMultipart()
        mime_message.attach(MIMEText(body, "html"))
        mime_message["To"] = to
        mime_message["Subject"] = subject
        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        return {"raw": encoded_message} 