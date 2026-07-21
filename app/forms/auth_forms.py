"""WTForms for authentication and account management."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, ValidationError, Optional
)

from app.models.user import User


class RegistrationForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=120)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters.")],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create Account")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.strip()).first():
            raise ValidationError("That username is already taken.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError("An account with that email already exists.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class ProfileUpdateForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=120)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    currency = StringField("Currency", validators=[Optional(), Length(max=10)])
    monthly_budget = StringField("Monthly Budget", validators=[Optional()])
    submit = SubmitField("Save Changes")

    def __init__(self, current_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_user = current_user

    def validate_username(self, field):
        existing = User.query.filter_by(username=field.data.strip()).first()
        if existing and existing.id != self._current_user.id:
            raise ValidationError("That username is already taken.")

    def validate_email(self, field):
        existing = User.query.filter_by(email=field.data.strip().lower()).first()
        if existing and existing.id != self._current_user.id:
            raise ValidationError("An account with that email already exists.")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password", validators=[DataRequired(), Length(min=8, message="At least 8 characters.")]
    )
    confirm_new_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match.")],
    )
    submit = SubmitField("Change Password")
