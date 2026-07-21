"""Handles secure receipt image/file uploads."""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def save_receipt(file_storage):
    """Save an uploaded receipt file with a unique, sanitized filename.

    Returns the stored filename (relative to the uploads folder), or None
    if no file was provided.
    """
    if not file_storage or file_storage.filename == "":
        return None

    if not allowed_file(file_storage.filename):
        raise ValueError("Unsupported file type.")

    original = secure_filename(file_storage.filename)
    ext = original.rsplit(".", 1)[-1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    dest_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
    file_storage.save(dest_path)
    return unique_name


def delete_receipt(filename):
    """Remove a receipt file from disk if it exists."""
    if not filename:
        return
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(path):
        os.remove(path)
