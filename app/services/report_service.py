"""Aggregation queries powering the dashboard, reports, and Chart.js data."""
import calendar
from datetime import date
from sqlalchemy import func, extract

from app.extensions import db
from app.models.transaction import Transaction
from app.models.category import Category


def get_totals(user_id, start_date=None, end_date=None):
    """Return total income, total expense, and balance for a user,
    optionally restricted to a date range."""
    query = db.session.query(
        Transaction.type, func.coalesce(func.sum(Transaction.amount), 0.0)
    ).filter(Transaction.user_id == user_id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    results = dict(query.group_by(Transaction.type).all())
    income = results.get("income", 0.0)
    expense = results.get("expense", 0.0)
    return {
        "income": round(income, 2),
        "expense": round(expense, 2),
        "balance": round(income - expense, 2),
    }


def get_recent_transactions(user_id, limit=5):
    return (
        Transaction.query.filter_by(user_id=user_id)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .limit(limit)
        .all()
    )


def get_current_month_summary(user_id):
    today = date.today()
    start = date(today.year, today.month, 1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end = date(today.year, today.month, last_day)
    totals = get_totals(user_id, start, end)
    totals["month_name"] = today.strftime("%B %Y")
    return totals


def get_category_breakdown(user_id, tx_type="expense", start_date=None, end_date=None):
    """Category-wise totals for the pie chart."""
    query = (
        db.session.query(Category.name, func.coalesce(func.sum(Transaction.amount), 0.0))
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(Transaction.user_id == user_id, Transaction.type == tx_type)
    )
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    rows = query.group_by(Category.name).order_by(func.sum(Transaction.amount).desc()).all()
    return {"labels": [r[0] for r in rows], "values": [round(r[1], 2) for r in rows]}


def get_monthly_income_vs_expense(user_id, months_back=6):
    """Bar chart data: income vs expense per month for the last N months."""
    today = date.today()
    labels, income_data, expense_data = [], [], []

    # Build list of the last `months_back` (year, month) pairs, oldest first
    y, m = today.year, today.month
    periods = []
    for _ in range(months_back):
        periods.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    periods.reverse()

    for (yr, mo) in periods:
        totals = (
            db.session.query(Transaction.type, func.coalesce(func.sum(Transaction.amount), 0.0))
            .filter(
                Transaction.user_id == user_id,
                extract("year", Transaction.date) == yr,
                extract("month", Transaction.date) == mo,
            )
            .group_by(Transaction.type)
            .all()
        )
        totals = dict(totals)
        labels.append(f"{calendar.month_abbr[mo]} {yr}")
        income_data.append(round(totals.get("income", 0.0), 2))
        expense_data.append(round(totals.get("expense", 0.0), 2))

    return {"labels": labels, "income": income_data, "expense": expense_data}


def get_spending_trend(user_id, days=30):
    """Line chart data: daily expense totals for the trend line."""
    rows = (
        db.session.query(Transaction.date, func.coalesce(func.sum(Transaction.amount), 0.0))
        .filter(Transaction.user_id == user_id, Transaction.type == "expense")
        .group_by(Transaction.date)
        .order_by(Transaction.date.asc())
        .all()
    )
    # Only keep the most recent `days` distinct entries
    rows = rows[-days:]
    labels = [r[0].strftime("%b %d") for r in rows]
    values = [round(r[1], 2) for r in rows]
    return {"labels": labels, "values": values}
