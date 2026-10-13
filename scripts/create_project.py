#!/usr/bin/env python3
"""Copy the tested starter into a new directory without overwriting existing work."""

import argparse
import os
import re
import secrets
import shutil
from pathlib import Path


def create_project(destination: Path, *, name: str, mode: str) -> Path:
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,62}", name):
        raise ValueError("Nama proyek harus slug lowercase, 1–63 karakter, dimulai huruf.")
    if mode not in {"fullstack", "api", "hybrid"}:
        raise ValueError("Mode harus fullstack, api, atau hybrid.")
    source = Path(__file__).resolve().parents[1] / "assets" / "boilerplate"
    target = destination.expanduser().resolve()
    if target == source or source in target.parents:
        raise ValueError("Destination tidak boleh berada dalam template boilerplate.")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir()  # Exclusive creation: even an existing empty directory is refused.
    shutil.copytree(
        source,
        target,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(
            ".venv",
            ".env",
            "__pycache__",
            "*.pyc",
            "*.sqlite3",
            ".ruff_cache",
            "staticfiles",
            "media",
            "output",
        ),
    )
    manifest = target / "pyproject.toml"
    manifest.write_text(
        manifest.read_text().replace('name = "django-starter"', f'name = "{name}"', 1)
    )
    lockfile = target / "uv.lock"
    lockfile.write_text(
        lockfile.read_text().replace('name = "django-starter"', f'name = "{name}"', 1)
    )
    secret_file = target / ".env"
    fd = os.open(secret_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as stream:
        stream.write(f"DJANGO_SECRET_KEY={secrets.token_urlsafe(50)}\n")
        stream.write(f"APP_NAME={name}\nAPP_MODE={mode}\nDEBUG=True\n")
        stream.write("ALLOWED_HOSTS=localhost,127.0.0.1\n")
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--name", default="django-app")
    parser.add_argument("--mode", choices=["fullstack", "api", "hybrid"], default="hybrid")
    args = parser.parse_args()
    try:
        target = create_project(args.destination, name=args.name, mode=args.mode)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Tidak dapat membuat proyek: {error}\n")
    print(f"Proyek dibuat di {target}; secret lokal ditulis privat tanpa ditampilkan.")
    print(
        "Lanjutkan: uv sync --locked, uv run python manage.py migrate, lalu createsuperuser/runserver."
    )


if __name__ == "__main__":
    main()
