#!/usr/bin/env python3
"""Generate a local development secret without displaying or replacing it."""

import argparse
import os
from pathlib import Path
from secrets import token_urlsafe

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["fullstack", "api", "hybrid"], default="hybrid")
    args = parser.parse_args()
    target = Path(__file__).resolve().parents[1] / ".env"
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        parser.exit(1, ".env sudah ada; secret tidak diubah.\n")
    with os.fdopen(fd, "w") as stream:
        stream.write(f"DJANGO_SECRET_KEY={token_urlsafe(50)}\n")
        stream.write(f"APP_NAME=Django Starter\nAPP_MODE={args.mode}\nDEBUG=True\n")
        stream.write("ALLOWED_HOSTS=localhost,127.0.0.1\n")
    print(".env lokal dibuat dengan izin privat; secret tidak ditampilkan.")
