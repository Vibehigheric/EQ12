"""Google Drive connector with local fallback."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

try:
    from google.oauth2.service_account import Credentials  # type: ignore
    from googleapiclient.discovery import build  # type: ignore
    from googleapiclient.http import MediaFileUpload  # type: ignore
except ImportError:  # pragma: no cover
    Credentials = None  # type: ignore
    build = None  # type: ignore
    MediaFileUpload = None  # type: ignore


class DriveConnector:
    """Uploads artifacts to Google Drive or local storage when offline."""

    def __init__(self, config: dict, base_dir: Path):
        self.base_dir = base_dir
        self.enabled = config.get("enabled", False)
        self.credentials_path = config.get("credentials_path")
        self.default_folder_id = config.get("folder_id")
        self.export_dir = base_dir / "drive_exports"
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def _build_service(self):
        if not self.enabled or not self.credentials_path or not Credentials or not build:
            return None
        cred_path = Path(self.credentials_path)
        if not cred_path.exists():
            return None
        scopes = ["https://www.googleapis.com/auth/drive.file"]
        creds = Credentials.from_service_account_file(str(cred_path), scopes=scopes)
        return build("drive", "v3", credentials=creds)

    def upload(
        self,
        file_path: Path,
        folder_id: str | None = None,
        description: str | None = None,
    ) -> Path:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(file_path)

        service = self._build_service()
        if service and MediaFileUpload:
            metadata = {"name": file_path.name}
            if folder_id or self.default_folder_id:
                metadata["parents"] = [folder_id or self.default_folder_id]
            try:
                media = MediaFileUpload(str(file_path), resumable=False)
                service.files().create(body=metadata, media_body=media, fields="id").execute()
            except Exception:
                pass

        destination = self.export_dir / file_path.name
        shutil.copy2(file_path, destination)
        if description:
            meta = {"description": description, "source": str(file_path)}
            destination.with_suffix(destination.suffix + ".meta.json").write_text(
                json.dumps(meta, indent=2), encoding="utf-8"
            )
        return destination


def build_drive_connector(config: dict, base_dir: Path) -> DriveConnector:
    return DriveConnector(config.get("drive", {}), base_dir)
