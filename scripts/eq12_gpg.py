"""
Python wrappers for GPG operations to integrate with EQ12.
Provides:
 - encrypt_file(path, recipient=None, sign=False)
 - decrypt_file(path, output=None)
 - clearsign_file(path)
 - verify_signature(path)

Requires `python-gnupg` package for higher-level operations, or falls back to subprocess calls to `gpg`.
"""

import os
import subprocess

GPG_PATH = "gpg"


def _run_gpg(args):
    cmd = [GPG_PATH, *args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def encrypt_file(path, recipient, sign=False, armor=False, output=None):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    args = []
    if armor:
        args.append("--armor")
    args.extend(["--encrypt", "--recipient", recipient])
    if sign:
        args.append("--sign")
    if output:
        args.extend(["--output", output])
    args.append(path)
    return _run_gpg(args)


def decrypt_file(path, output=None):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    args = ["--yes", "--output", output or "-", "--decrypt", path]
    return _run_gpg(args)


def clearsign_file(path, output=None):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    out = output or f"{path}.asc"
    args = ["--clearsign", "--output", out, path]
    return _run_gpg(args)


def verify_signature(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    args = ["--verify", path]
    return _run_gpg(args)
