"""Category model — predefined + user-created custom categories."""
from datetime import datetime
from app.extensions import db

# Predefined categories seeded for every new user
DEFAULT_CATEGORIES = [
    ("Salary", "income", "bi-cash-coin"),
    ("Investment", "income", "bi-graph-up-arrow"),
    ("Food", "expense", "bi-cup-straw"),
    ("Transport", "expense", "bi-bus-front"),
    ("Shopping", "expense", "bi-bag"),
    ("Entertainment", "expense", "bi-film"),
    ("Healthcare", "expense", "bi-heart-pulse"),
    ("Education", "expense", "bi-book"),
    ("Bills", "expense", "bi-receipt"),
    ("Others", "expense", "bi-three-dots"),
]


class Category(db.Model):
    """A transaction category, either a system default or user-defined."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    icon = db.Column(db.String(50), default="bi-tag")
    is_default = db.Column(db.Boolean, default=False)  # seeded system category
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship("Transaction", backref="category", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint("name", "user_id", "type", name="uq_category_per_user"),
    )

    def __repr__(self):
        return f"<Category {self.name} ({self.type})>"
