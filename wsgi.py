"""WSGI entrypoint for production servers (e.g. gunicorn)."""

from src.main import create_app

app = create_app()
