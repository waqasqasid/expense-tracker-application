"""Seeding helpers — create default categories for a new user."""
from app.extensions import db
from app.models.category import Category, DEFAULT_CATEGORIES


def create_default_categories_for_user(user_id):
    """Create the standard set of predefined categories owned by `user_id`.

    Each user gets their own copy so they can freely rename/delete
    without affecting other users.
    """
    for name, cat_type, icon in DEFAULT_CATEGORIES:
        category = Category(
            name=name, type=cat_type, icon=icon, is_default=True, user_id=user_id
        )
        db.session.add(category)
    db.session.commit()


def seed_default_categories():
    """CLI helper — no-op placeholder retained for future global seeding."""
    pass
