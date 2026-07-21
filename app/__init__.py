"""
Application factory for the Personal Expense Tracker.
Follows the Flask application-factory pattern with Blueprints for
modular routing (Controller layer of MVC), SQLAlchemy models (Model layer),
and Jinja2 templates (View layer).
"""
import os
from flask import Flask, render_template

from config import config_by_name
from app.extensions import db, login_manager, migrate, csrf


def create_app(config_name=None):
    """Application factory.

    Args:
        config_name: 'development' | 'production' | 'testing'
    """
    config_name = config_name or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name[config_name])

    # Ensure instance & upload folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # --- Initialize extensions ---
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # --- Import models so Flask-Migrate can detect them ---
    from app.models.user import User  # noqa: F401
    from app.models.category import Category  # noqa: F401
    from app.models.transaction import Transaction  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Register Blueprints ---
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.transactions import transactions_bp
    from app.routes.reports import reports_bp
    from app.routes.categories import categories_bp
    from app.routes.profile import profile_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(transactions_bp, url_prefix="/transactions")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(categories_bp, url_prefix="/categories")
    app.register_blueprint(profile_bp, url_prefix="/profile")

    # --- Error handlers ---
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.errorhandler(413)
    def file_too_large(error):
        from flask import flash, redirect, request
        flash("File is too large. Maximum upload size is 5 MB.", "danger")
        return redirect(request.referrer or "/"), 302

    # --- Jinja global helpers / context processors ---
    from datetime import datetime

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.utcnow().year}

    # --- CLI command to seed default categories ---
    @app.cli.command("seed-categories")
    def seed_categories():
        """Seed default global categories (run: flask seed-categories)."""
        from app.services.seed_service import seed_default_categories
        seed_default_categories()
        print("Default categories seeded.")

    return app
