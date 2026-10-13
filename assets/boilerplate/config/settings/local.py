from pathlib import Path

import environ

environ.Env.read_env(Path(__file__).resolve().parents[2] / ".env")
from .base import *  # noqa: E402

DEBUG = env.bool("DEBUG", default=True)
DATABASES = {"default": env.db(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}
