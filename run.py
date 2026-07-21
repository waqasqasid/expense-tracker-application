"""
Entry point for running the Flask development server.

Usage:
    python run.py

For production, use a WSGI server instead, e.g.:
    gunicorn "run:app"
"""
import os
from dotenv import load_dotenv

load_dotenv()  # populate os.environ from a local .env file, if present

from app import create_app  # noqa: E402

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True), host="0.0.0.0", port=5000)
