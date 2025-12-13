#!/usr/bin/env python3
"""eq12_cleanup.py
Performs conservative cleanup: moves sensitive files into keys/, archives duplicates/backups to archive_duplicates/, updates .gitignore,
and regenerates a concise inventory file `eq12_inventory.txt`.
Run on Windows (paths are Windows-style).
"""

import difflib
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(r"C:\EQ12")
KEYS_DIR = BASE / "keys"
ARCHIVE_DUP = BASE / "archive_duplicates"
DATA_ARCHIVE = BASE / "data" / "archive"
GITIGNORE = BASE / ".gitignore"
INVENTORY = BASE / "eq12_inventory.txt"
REPORT = BASE / "eq12_cleanup_report.txt"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

SENSITIVE_REL = [Path("EdgeGodParlays") / "creds.json", Path("EdgeGodParlays") / ".env"]
DUP_PATTERNS = [" - Copy", ".bak", "~", ".old"]

logs = []
errors = []
actions = []


def ensure(p: Path) -> None:
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)


def move_with_collision(src: Path, dst_dir: Path) -> None:
    ensure(dst_dir)
    dst = dst_dir / src.name
    if dst.exists():
        stem = src.stem
        suf = src.suffix
        dst = dst_dir / f"{stem}_{TIMESTAMP}{suf}"
    try:
        shutil.move(str(src), str(dst))
        actions.append(f"moved: {src} -> {dst}")
        return dst
    except Exception as e:
        errors.append(f"failed to move {src}: {e}")
        return None


def append_gitignore(lines) -> None:
    existing = set()
    if GITIGNORE.exists():
        existing = {
            l.strip() for l in GITIGNORE.read_text(encoding="utf-8").splitlines() if l.strip()
        }
    to_add = [l for l in lines if l not in existing]
    if to_add:
        with GITIGNORE.open("a", encoding="utf-8") as f:
            for l in to_add:
                f.write(l + "\n")
        actions.append(f"updated .gitignore (+{len(to_add)} lines)")
    else:
        actions.append(".gitignore already contains entries; no change")


def archive_duplicates() -> None:
    # Walk tree and find files matching patterns; move them to ARCHIVE_DUP preserving relative path
    for p in BASE.rglob("*"):
        if p.is_file():
            name = p.name
            # skip files already in keys or archive directories
            if any(part in ("keys", "archive_duplicates", "data\\archive") for part in p.parts):
                continue
            match = False
            for pat in DUP_PATTERNS:
                if pat in name:
                    match = True
                    break
            if match:
                rel = p.relative_to(BASE)
                dest_dir = ARCHIVE_DUP / rel.parent
                ensure(dest_dir)
                dst = dest_dir / p.name
                # if counterpart exists (e.g., "file - Copy.ext" and "file.ext") produce a small diff
                # detect original name by removing known suffix patterns like ' - Copy'
                orig_candidates = []
                if " - Copy" in name:
                    orig_name = name.replace(" - Copy", "")
                    orig_candidates.append(orig_name)
                # also consider .bak -> original without .bak
                if name.endswith(".bak"):
                    orig_candidates.append(name[:-4])
                orig_path = None
                for cand in orig_candidates:
                    cand_path = p.with_name(cand)
                    if cand_path.exists():
                        orig_path = cand_path
                        break
                if orig_path and orig_path.is_file():
                    # write a diff file in the same archive folder
                    try:
                        a_txt = orig_path.read_text(errors="ignore", encoding="utf-8").splitlines()
                        b_txt = p.read_text(errors="ignore", encoding="utf-8").splitlines()
                        diff = difflib.unified_diff(
                            a_txt,
                            b_txt,
                            fromfile=str(orig_path),
                            tofile=str(p),
                            lineterm="",
                        )
                        diff_text = "\n".join(list(diff))
                        if diff_text:
                            diff_file = dest_dir / (p.name + ".diff.txt")
                            diff_file.write_text(diff_text, encoding="utf-8")
                            actions.append(f"wrote diff: {diff_file}")
                    except Exception as e:
                        errors.append(f"diff failed for {p}: {e}")
                # move file
                try:
                    shutil.move(str(p), str(dst))
                    actions.append(f"archived duplicate: {p} -> {dst}")
                except Exception as e:
                    errors.append(f"failed to archive {p}: {e}")


def move_sensitive() -> None:
    ensure(KEYS_DIR)
    for rel in SENSITIVE_REL:
        src = BASE / rel
        if src.exists():
            move_with_collision(src, KEYS_DIR)
        else:
            logs.append(f"not found (no-op): {src}")


def regen_inventory() -> None:
    # produce concise inventory: keep top-level scripts, EdgeGodParlays entrypoints, and data/report files
    lines = []
    lines.append("EQ12 inventory (generated)")
    lines.append("Generated: " + datetime.now().isoformat())
    lines.append("")
    lines.append("Kept:")
    # scan a few known locations
    candidates = [BASE, BASE / "EdgeGodParlays", BASE / "data", BASE / "dashboard"]
    added = set()
    for c in candidates:
        if c.exists():
            for p in c.iterdir():
                if p.is_dir():
                    lines.append(f"- {p}")
                else:
                    if (
                        p.suffix in (".ps1", ".py", ".xml", ".json", ".csv", ".html")
                        or p.name.lower().startswith("eq12_")
                        or "launcher" in p.name.lower()
                    ):
                        rel = p.relative_to(BASE)
                        if rel not in added:
                            lines.append(f"- {p}")
                            added.add(rel)
    lines.append("")
    lines.append("Sensitive (moved):")
    for s in SENSITIVE_REL:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("Archived duplicates: see archive_duplicates/")
    INVENTORY.write_text("\n".join(lines), encoding="utf-8")
    actions.append(f"regenerated inventory: {INVENTORY}")


def main() -> None:
    try:
        ensure(KEYS_DIR)
        ensure(ARCHIVE_DUP)
        ensure(DATA_ARCHIVE)
        # Normal run performs actions. If caller wants verification only, they can pass '--verify'
        if "--verify" in sys.argv:
            # Report current state without moving files
            actions.append("verify-only: listing current keys/ and archive_duplicates/")
        else:
            move_sensitive()
            archive_duplicates()
            append_gitignore(
                [
                    str(p.as_posix())
                    for p in [
                        Path("EdgeGodParlays/creds.json"),
                        Path("EdgeGodParlays/.env"),
                        Path("keys/"),
                    ]
                ]
            )
            regen_inventory()
        # write report
        out = []
        out.append("EQ12 cleanup report")
        out.append("Generated: " + datetime.now().isoformat())
        out.append("")
        out.append("Actions:")
        out.extend(actions or ["(none)"])
        out.append("")
        out.append("Logs:")
        out.extend(logs or ["(none)"])
        if errors:
            out.append("")
            out.append("Errors:")
            out.extend(errors)
        REPORT.write_text("\n".join(out), encoding="utf-8")
        print("\n".join(out))
    except Exception as e:
        print("fatal error:", e)
        sys.exit(2)


if __name__ == "__main__":
    main()
