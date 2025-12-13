"""EQ12 Google Drive integration skeleton.

This module provides a thin wrapper around Google Drive operations with a local-only
archive fallback so unit tests can run without credentials.

Functions:
- upload_file(local_path, drive_folder_id)
- download_file(file_id, local_path)
- list_files(drive_folder_id)
- archive_logs(logs_dir, archive_folder)

If GOOGLE_DRIVE_CLIENT_ID / SECRET and oauth credentials are provided, the real
Drive upload/download functions can be implemented using google-auth and
google-api-python-client. For now, the skeleton logs actions and archive_logs
moves old logs into an archive folder.
"""

from __future__ import annotations

import argparse
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

LOG = logging.getLogger("eq12_drive")


def upload_file(local_path: str, drive_folder_id: str) -> str | None:
    """Upload a file to Google Drive. Returns file ID on success.

    This is a placeholder: when credentials are configured, implement using
    googleapiclient.discovery build + MediaFileUpload.
    """
    p = Path(local_path)
    if not p.exists():
        LOG.error("Local file not found: %s", local_path)
        return None
    LOG.info("(placeholder) Upload %s to Drive folder %s", local_path, drive_folder_id)
    # return a fake file id for testing
    return f"local-{p.name}-{int(p.stat().st_mtime)}"


def download_file(file_id: str, local_path: str) -> bool:
    """Placeholder download. Returns True on success."""
    LOG.info("(placeholder) Download file id %s to %s", file_id, local_path)
    # nothing to do
    Path(local_path).write_text(f"Downloaded placeholder for {file_id}\n")
    return True


def list_files(drive_folder_id: str) -> list[dict]:
    LOG.info("(placeholder) Listing files in folder %s", drive_folder_id)
    return []


def archive_logs(logs_dir: str, archive_folder: str, older_than_days: int = 7) -> int:
    """Move logs older than `older_than_days` from logs_dir to archive_folder.

    Returns number of files moved.
    """
    src = Path(logs_dir)
    dst_root = Path(archive_folder)
    if not src.exists():
        LOG.warning("Logs dir does not exist: %s", logs_dir)
        return 0
    dst_root.mkdir(parents=True, exist_ok=True)

    cutoff = datetime.utcnow() - timedelta(days=older_than_days)
    moved = 0
    for p in src.iterdir():
        if p.is_file():
            mtime = datetime.utcfromtimestamp(p.stat().st_mtime)
            if mtime < cutoff:
                dst = dst_root / p.name
                shutil.move(str(p), str(dst))
                moved += 1
                LOG.info("Archived %s -> %s", p, dst)
    return moved


def main(argv=None) -> bool:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")

    up = sub.add_parser("upload")
    up.add_argument("local_path")
    up.add_argument("drive_folder_id")

    dl = sub.add_parser("download")
    dl.add_argument("file_id")
    dl.add_argument("local_path")

    ls = sub.add_parser("list")
    ls.add_argument("drive_folder_id")

    ar = sub.add_parser("archive_logs")
    ar.add_argument("logs_dir")
    ar.add_argument("archive_folder")
    ar.add_argument("--days", type=int, default=7)

    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO)

    if args.cmd == "upload":
        LOG.info(upload_file(args.local_path, args.drive_folder_id))
    elif args.cmd == "download":
        LOG.info(download_file(args.file_id, args.local_path))
    elif args.cmd == "list":
        LOG.info(list_files(args.drive_folder_id))
    elif args.cmd == "archive_logs":
        moved = archive_logs(args.logs_dir, args.archive_folder, older_than_days=args.days)
        LOG.info(moved)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
