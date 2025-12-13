import base64
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def gmail_service():
    """Launches local browser for OAuth consent the first run.
    Expects a 'credentials.json' in the working directory."""
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return build("gmail", "v1", credentials=creds)


def _build_message(to, subject, body, attachments=None):
    if attachments:
        msg = MIMEMultipart()
        msg["to"] = to
        msg["subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        for path in attachments:
            if not os.path.exists(path):
                continue
            part = MIMEBase("application", "octet-stream")
            with open(path, "rb") as f:
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(path)}")
            msg.attach(part)
        return msg
    msg = MIMEText(body, "plain")
    msg["to"] = to
    msg["subject"] = subject
    return msg


def send_email(service, to, subject, body, attachments=None):
    message = _build_message(to, subject, body, attachments)
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()
