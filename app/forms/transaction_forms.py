"""WTForms for creating/editing transactions and filtering the list/reports."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, FloatField, SelectField, DateField, TextAreaField, SubmitField
)
from wtforms.validators import DataRequired, NumberRange, Optional, Length

from app.models.transaction import PAYMENT_METHODS


class TransactionForm(FlaskForm):
    type = SelectField(
        "Type", choices=[("income", "Income"), ("expense", "Expense")], validators=[DataRequired()]
    )
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    amount = FloatField("Amount", validators=[DataRequired(), NumberRange(min=0.01, message="Amount must be greater than 0.")])
    date = DateField("Date", validators=[DataRequired()])
    payment_method = SelectField(
        "Payment Method",
        choices=[(m, m) for m in PAYMENT_METHODS],
        validators=[DataRequired()],
    )
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=500)])
    receipt = FileField(
        "Receipt Image (optional)",
        validators=[FileAllowed(["png", "jpg", "jpeg", "gif", "pdf"], "Images or PDF only!")],
    )
    submit = SubmitField("Save Transaction")


class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired(), Length(min=2, max=80)])
    type = SelectField(
        "Type", choices=[("income", "Income"), ("expense", "Expense")], validators=[DataRequired()]
    )
    icon = StringField("Icon (Bootstrap Icon class)", validators=[Optional(), Length(max=50)], default="bi-tag")
    submit = SubmitField("Save Category")


class TransactionFilterForm(FlaskForm):
    """Non-CSRF-enforced GET filter form for transaction list / reports."""
    class Meta:
        csrf = False

    search = StringField("Search", validators=[Optional()])
    type = SelectField(
        "Type",
        choices=[("", "All"), ("income", "Income"), ("expense", "Expense")],
        validators=[Optional()],
    )
    category_id = SelectField("Category", coerce=int, validators=[Optional()])
    payment_method = SelectField(
        "Payment Method",
        choices=[("", "All")] + [(m, m) for m in PAYMENT_METHODS],
        validators=[Optional()],
    )
    date_from = DateField("From", validators=[Optional()])
    date_to = DateField("To", validators=[Optional()])
    amount_min = FloatField("Min Amount", validators=[Optional()])
    amount_max = FloatField("Max Amount", validators=[Optional()])
    month = SelectField("Month", validators=[Optional()])
    year = SelectField("Year", validators=[Optional()])
    sort_by = SelectField(
        "Sort By",
        choices=[
            ("date_desc", "Date (Newest)"),
            ("date_asc", "Date (Oldest)"),
            ("amount_desc", "Amount (High-Low)"),
            ("amount_asc", "Amount (Low-High)"),
        ],
        validators=[Optional()],
    )
    submit = SubmitField("Apply Filters")
