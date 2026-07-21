"""Profile management: update personal info, change password, app settings."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from app.extensions import db
from app.forms.auth_forms import ProfileUpdateForm, ChangePasswordForm

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = ProfileUpdateForm(current_user, obj=current_user)
    password_form = ChangePasswordForm()

    if form.submit.data and form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.username = form.username.data.strip()
        current_user.email = form.email.data.strip().lower()
        current_user.phone = form.phone.data.strip() if form.phone.data else None
        current_user.currency = form.currency.data.strip() if form.currency.data else "USD"
        try:
            current_user.monthly_budget = float(form.monthly_budget.data) if form.monthly_budget.data else 0.0
        except ValueError:
            current_user.monthly_budget = 0.0
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile.index"))

    return render_template("profile/index.html", form=form, password_form=password_form)


@profile_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password changed successfully!", "success")
    else:
        for field_errors in form.errors.values():
            for err in field_errors:
                flash(err, "danger")
    return redirect(url_for("profile.index"))


@profile_bp.route("/settings")
@login_required
def settings():
    return render_template("profile/settings.html")


@profile_bp.route("/settings/theme", methods=["POST"])
@login_required
def toggle_theme():
    """AJAX endpoint to persist the user's dark/light mode preference."""
    theme = request.json.get("theme") if request.is_json else request.form.get("theme")
    if theme not in ("light", "dark"):
        return jsonify({"success": False, "message": "Invalid theme."}), 400
    current_user.theme_preference = theme
    db.session.commit()
    return jsonify({"success": True, "theme": theme})
