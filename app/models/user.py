"""User model — handles authentication and profile data."""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    """Represents an application user.

    UserMixin supplies is_authenticated / is_active / is_anonymous / get_id
    required by Flask-Login.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    currency = db.Column(db.String(10), default="USD", nullable=False)
    theme_preference = db.Column(db.String(10), default="light", nullable=False)  # light/dark
    profile_image = db.Column(db.String(255), default="default_avatar.png")
    monthly_budget = db.Column(db.Float, default=0.0)
    is_active_account = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = db.relationship(
        "Transaction", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    categories = db.relationship(
        "Category", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )

    # --- Password helpers ---
    def set_password(self, raw_password):
        """Hash and store the given plaintext password."""
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, raw_password)

    # Flask-Login requires get_id to return a string; UserMixin does this
    # automatically from self.id, so no override needed.

    def __repr__(self):
        return f"<User {self.username}>"
