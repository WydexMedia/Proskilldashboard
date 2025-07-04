import os
import base64
from pathlib import Path
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request                    # ← import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# adjust these paths if needed
BASE_DIR         = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = BASE_DIR / 'credentials.json'
TOKEN_PATH       = BASE_DIR / 'token.json'

def get_gmail_service():
    creds = None

    # 1) load existing token.json
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    # 2) if no valid creds, either refresh or run the flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())                                # ← refresh with Request()
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH),
                SCOPES,
                redirect_uri='http://localhost:62932/'             # ← must match your GCP setting
            )
            creds = flow.run_local_server(port=62932)               # ← use the exact port you registered

        # save (or overwrite) token.json
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())

    # 3) build Gmail client
    return build('gmail', 'v1', credentials=creds)

def send_gmail_api_mail(subject: str, body: str, to_email: str, from_email: str = None):
    service = get_gmail_service()

    mime_msg = MIMEText(body)
    mime_msg['to'] = to_email
    mime_msg['subject'] = subject
    if from_email:
        mime_msg['from'] = from_email

    raw = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()
    return service.users().messages().send(
        userId='me',
        body={'raw': raw}
    ).execute()
