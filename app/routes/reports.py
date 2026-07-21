"""Monthly financial reports with filters, charts, and export/print options."""
import calendar
from datetime import date

from flask import Blueprint, render_template, request, send_file
from flask_login import login_required, current_user

from app.models.transaction import Transaction
from app.models.category import Category
from app.services import report_service
from app.services.export_service import export_transactions_csv, export_transactions_pdf

reports_bp = Blueprint("reports", __name__)


def _get_period_transactions(user_id, year, month, category_id=None, tx_type=None):
    query = Transaction.query.filter_by(user_id=user_id)
    if year:
        query = query.filter(Transaction.date >= date(year, 1, 1))
        if month:
            last_day = calendar.monthrange(year, month)[1]
            query = query.filter(
                Transaction.date >= date(year, month, 1), Transaction.date <= date(year, month, last_day)
            )
        else:
            query = query.filter(Transaction.date <= date(year, 12, 31))
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if tx_type:
        query = query.filter(Transaction.type == tx_type)
    return query.order_by(Transaction.date.desc()).all()


def _resolve_filters():
    today = date.today()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)
    category_id = request.args.get("category_id", type=int)
    tx_type = request.args.get("type", "").strip() or None
    return year, month, category_id, tx_type


@reports_bp.route("/")
@login_required
def index():
    year, month, category_id, tx_type = _resolve_filters()
    transactions = _get_period_transactions(current_user.id, year, month, category_id, tx_type)

    start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])
    summary = report_service.get_totals(current_user.id, start, end)
    category_breakdown = report_service.get_category_breakdown(current_user.id, "expense", start, end)
    monthly_comparison = report_service.get_monthly_income_vs_expense(current_user.id, months_back=6)

    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    years_available = sorted(
        {t.date.year for t in Transaction.query.filter_by(user_id=current_user.id).all()} | {today_year()},
        reverse=True,
    )

    return render_template(
        "reports/index.html",
        transactions=transactions,
        summary=summary,
        category_breakdown=category_breakdown,
        monthly_comparison=monthly_comparison,
        categories=categories,
        selected_year=year,
        selected_month=month,
        selected_category=category_id,
        selected_type=tx_type,
        years_available=years_available,
        month_name=calendar.month_name[month],
    )


def today_year():
    return date.today().year


@reports_bp.route("/export/csv")
@login_required
def export_csv():
    year, month, category_id, tx_type = _resolve_filters()
    transactions = _get_period_transactions(current_user.id, year, month, category_id, tx_type)
    csv_file = export_transactions_csv(transactions)
    return send_file(
        csv_file,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"report_{year}_{month:02d}.csv",
    )


@reports_bp.route("/export/pdf")
@login_required
def export_pdf():
    year, month, category_id, tx_type = _resolve_filters()
    transactions = _get_period_transactions(current_user.id, year, month, category_id, tx_type)
    start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])
    summary = report_service.get_totals(current_user.id, start, end)
    title = f"Monthly Report — {calendar.month_name[month]} {year}"
    pdf_file = export_transactions_pdf(transactions, current_user, title=title, summary=summary)
    return send_file(
        pdf_file,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"report_{year}_{month:02d}.pdf",
    )


@reports_bp.route("/print")
@login_required
def print_report():
    year, month, category_id, tx_type = _resolve_filters()
    transactions = _get_period_transactions(current_user.id, year, month, category_id, tx_type)
    start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])
    summary = report_service.get_totals(current_user.id, start, end)
    return render_template(
        "reports/print.html",
        transactions=transactions,
        summary=summary,
        month_name=calendar.month_name[month],
        year=year,
    )
