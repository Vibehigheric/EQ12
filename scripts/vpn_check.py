#!/usr/bin/env python3
r"""Validate WireGuard configuration and emit JSON status for EQ12.

Reads WIREGUARD_CONFIG environment variable (can be full conf content or path).
Writes a JSON snapshot to C:\EQ12\logs\vpn_status.json
"""

from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
from pathlib import Path


def load_config() -> bool:
    cfg = os.environ.get("WIREGUARD_CONFIG")
    if not cfg:
        return None
    p = Path(cfg)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return cfg


def looks_like_wg(conf: str) -> bool:
    # naive checks for '[Interface]' or '[Peer]' blocks and 'PrivateKey' or 'PublicKey'
    if not conf:
        return False
    return bool(re.search(r"\[Interface\]|\[Peer\]|PrivateKey|PublicKey", conf, re.I))


def call_wg_show() -> bool:
    try:
        out = subprocess.check_output(["wg"], stderr=subprocess.STDOUT, text=True)
        return out
    except Exception as e:
        return str(e)


def write_status(status: dict) -> bool:
    logdir = Path("C:/EQ12/logs")
    logdir.mkdir(parents=True, exist_ok=True)
    out = logdir / "vpn_status.json"
    out.write_text(json.dumps(status, indent=2), encoding="utf-8")


def main() -> bool:
    conf = load_config()
    status = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "has_config": conf is not None,
        "looks_like_wireguard": looks_like_wg(conf) if conf else False,
        "wg_output": None,
    }
    # Attempt to call wg if available
    try:
        status["wg_output"] = call_wg_show()
    except Exception as e:
        status["wg_output"] = f"error: {e}"

    write_status(status)
    print("Wrote vpn_status.json")


if __name__ == "__main__":
    main()
