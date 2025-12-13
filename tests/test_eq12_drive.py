import os
import time
from pathlib import Path

from drive.eq12_drive import archive_logs


def touch(path: Path, days_old: int = 0) -> None:
    path.write_text("x")
    if days_old:
        atime = path.stat().st_atime
        mtime = path.stat().st_mtime - days_old * 86400
        os.utime(path, (atime, mtime))


def test_archive_logs(tmp_path) -> None:
    logs = tmp_path / "logs"
    arch = tmp_path / "archive"
    logs.mkdir()
    # create two files: one old, one recent
    old = logs / "old.log"
    new = logs / "new.log"
    old.write_text("old")
    new.write_text("new")
    # set old mtime to 10 days ago
    old_mtime = int(time.time()) - 10 * 86400
    os.utime(old, (old_mtime, old_mtime))

    moved = archive_logs(str(logs), str(arch), older_than_days=7)
    assert moved == 1
    assert not (logs / "old.log").exists()
    assert (arch / "old.log").exists()
