"""Email executor for EQ12 Commander++"""

from __future__ import annotations

import smtplib
from collections.abc import Iterable
from email.message import EmailMessage
from pathlib import Path

DEFAULT_SENDER = "eq12-commander@example.com"


class EmailExecutor:
    """Handles high-level email delivery with safe fallbacks."""

    def __init__(self, config: dict, base_dir: Path):
        self.base_dir = base_dir
        self.enabled = config.get("enabled", False)
        self.smtp_host = config.get("smtp_host", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username")
        self.password = config.get("password")
        self.default_recipient = config.get("default_recipient")
        self.sender = config.get("sender", self.username or DEFAULT_SENDER)
        self.outbox_dir = base_dir / "outbox"
        self.outbox_dir.mkdir(parents=True, exist_ok=True)

    def _build_message(
        self,
        subject: str,
        body: str,
        to: Iterable[str] | None = None,
        attachments: Iterable[Path] | None = None,
    ) -> EmailMessage:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.sender
        recipients = list(to or ([] if not self.default_recipient else [self.default_recipient]))
        if not recipients:
            raise ValueError("No recipients specified for email dispatch")
        msg["To"] = ", ".join(recipients)
        msg.set_content(body)

        attachments = attachments or []
        for attachment in attachments:
            attachment_path = Path(attachment)
            if not attachment_path.exists():
                continue
            data = attachment_path.read_bytes()
            msg.add_attachment(
                data,
                maintype="application",
                subtype="octet-stream",
                filename=attachment_path.name,
            )
        return msg

    def send_email(
        self,
        subject: str,
        body: str,
        to: Iterable[str] | None = None,
        attachments: Iterable[Path] | None = None,
        dry_run: bool = False,
    ) -> Path:
        message = self._build_message(subject, body, to, attachments)

        if not self.enabled or dry_run:
            return self._write_to_outbox(message, dry_run)

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as smtp:
                smtp.starttls()
                if self.username and self.password:
                    smtp.login(self.username, self.password)
                smtp.send_message(message)
            return self._write_to_outbox(message, dry_run=True)
        except Exception:
            return self._write_to_outbox(message, dry_run=True)

    def _write_to_outbox(self, message: EmailMessage, dry_run: bool) -> Path:
        suffix = "dry_run" if dry_run else "queued"
        subject = message["Subject"] or "no_subject"
        sanitized = subject.replace(" ", "_")[:40]
        filename = f"email_{suffix}_{sanitized}.eml"
        output_path = self.outbox_dir / filename
        output_path.write_text(message.as_string(), encoding="utf-8")
        return output_path


def build_email_executor(config: dict, base_dir: Path) -> EmailExecutor:
    return EmailExecutor(config.get("email", {}), base_dir)
