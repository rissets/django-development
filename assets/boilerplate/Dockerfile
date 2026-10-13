FROM ghcr.io/astral-sh/uv:0.9.26 AS uv
FROM python:3.12-slim
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
COPY . .
RUN DJANGO_SETTINGS_MODULE=config.settings.local DJANGO_SECRET_KEY=static-build-only-not-for-runtime DEBUG=False uv run --no-sync python manage.py collectstatic --noinput
RUN useradd --create-home --uid 10001 appuser && mkdir -p /app/media && chown -R appuser:appuser /app
USER appuser
ENV PATH="/app/.venv/bin:${PATH}" DJANGO_SETTINGS_MODULE=config.settings.production
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/', timeout=3)"
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-"]
