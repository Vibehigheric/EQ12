import logging

# Set up logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
r"""eq12_restore.py
Conservative restore tool: lists files in keys/ and lets you restore specific ones back to their original paths.
Usage: python eq12_restore.py --list
       python eq12_restore.py --restore creds.json
The script will only restore from keys/ back to the path relative to C:\EQ12 (it won't overwrite without prompting).
"""
import shutil
import sys
from pathlib import Path

BASE = Path(r"C:\EQ12")
KEYS = BASE / "keys"


def list_keys() -> None:
    if not KEYS.exists():
        print("keys/ not found")
        return
    for p in sorted(KEYS.rglob("*")):
        if p.is_file():
            logger.info(p.relative_to(KEYS))


def restore(name) -> None:
    candidates = list(KEYS.rglob(name))
    if not candidates:
        print("no matching file in keys/")
        return
    if len(candidates) > 1:
        print("multiple matches:")
        for i, p in enumerate(candidates):
            logger.info(i, p)
        return
    src = candidates[0]
    # original path guess: drop KEYS and use name under BASE/EdgeGodParlays or top-level
    # We will attempt to place it under its original relative path if we can guess it, otherwise ask the user
    # For creds.json and .env we expect EdgeGodParlays/
    dest = BASE / "EdgeGodParlays" / src.name
    if dest.exists():
        print(f"destination exists: {dest} - aborting")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    print(f"restored {src} -> {dest}")


if __name__ == "__main__":
    if "--list" in sys.argv:
        list_keys()
    elif "--restore" in sys.argv:
        idx = sys.argv.index("--restore")
        if idx + 1 < len(sys.argv):
            restore(sys.argv[idx + 1])
        else:
            print("specify filename to restore")
    else:
        print("usage: --list | --restore <filename>")
