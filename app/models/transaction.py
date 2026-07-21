"""Transaction model — an income or expense entry belonging to a user."""
from datetime import datetime
from app.extensions import db

PAYMENT_METHODS = ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "Mobile Wallet", "Other"]


class Transaction(db.Model):
    """A single income or expense record."""

    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow, index=True)
    payment_method = db.Column(db.String(30), nullable=False, default="Cash")
    notes = db.Column(db.Text, nullable=True)
    receipt_image = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction {self.type} {self.amount} on {self.date}>"

    def to_dict(self):
        """Serialize for JSON / CSV export."""
        return {
            "id": self.id,
            "type": self.type,
            "amount": self.amount,
            "category": self.category.name if self.category else "",
            "date": self.date.strftime("%Y-%m-%d") if self.date else "",
            "payment_method": self.payment_method,
            "notes": self.notes or "",
        }
