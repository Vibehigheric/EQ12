import base64
from email.mime.text import MIMEText

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def gmail_service():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return build("gmail", "v1", credentials=creds)


def send_email(service, to, subject, body):
    msg = MIMEText(body, "plain")
    msg["to"] = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()
