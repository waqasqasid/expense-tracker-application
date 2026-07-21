"""Dashboard route — the user's home base after login."""
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.services import report_service

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    totals = report_service.get_totals(current_user.id)
    month_summary = report_service.get_current_month_summary(current_user.id)
    recent_transactions = report_service.get_recent_transactions(current_user.id, limit=6)

    category_breakdown = report_service.get_category_breakdown(current_user.id, tx_type="expense")
    monthly_comparison = report_service.get_monthly_income_vs_expense(current_user.id, months_back=6)
    spending_trend = report_service.get_spending_trend(current_user.id, days=14)

    return render_template(
        "dashboard/index.html",
        totals=totals,
        month_summary=month_summary,
        recent_transactions=recent_transactions,
        category_breakdown=category_breakdown,
        monthly_comparison=monthly_comparison,
        spending_trend=spending_trend,
    )
