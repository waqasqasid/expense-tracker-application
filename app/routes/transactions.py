"""Transaction CRUD, search, filtering, sorting, and pagination."""
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from sqlalchemy import or_, extract

from app.extensions import db
from app.models.transaction import Transaction
from app.models.category import Category
from app.forms.transaction_forms import TransactionForm, TransactionFilterForm
from app.services.upload_service import save_receipt, delete_receipt
from app.services.export_service import export_transactions_csv

transactions_bp = Blueprint("transactions", __name__)


def _populate_category_choices(form, tx_type=None):
    """Fill the category <select> with the current user's categories.

    All categories (both income and expense) are included so the
    dropdown validates regardless of which type is selected client-side;
    main.js filters the visible <option>s by data-type to match the
    chosen transaction type.
    """
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.type, Category.name).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    # Stash extra metadata for the template to render data-type attributes
    form.category_id.category_objects = categories


def _apply_filters(query, args):
    """Apply search/filter/sort query-string params to a Transaction query."""
    search = args.get("search", "").strip()
    if search:
        like = f"%{search}%"
        query = query.join(Category).filter(
            or_(Transaction.notes.ilike(like), Category.name.ilike(like))
        )

    tx_type = args.get("type", "").strip()
    if tx_type in ("income", "expense"):
        query = query.filter(Transaction.type == tx_type)

    category_id = args.get("category_id", type=int)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    payment_method = args.get("payment_method", "").strip()
    if payment_method:
        query = query.filter(Transaction.payment_method == payment_method)

    date_from = args.get("date_from", "").strip()
    if date_from:
        try:
            query = query.filter(Transaction.date >= datetime.strptime(date_from, "%Y-%m-%d").date())
        except ValueError:
            pass

    date_to = args.get("date_to", "").strip()
    if date_to:
        try:
            query = query.filter(Transaction.date <= datetime.strptime(date_to, "%Y-%m-%d").date())
        except ValueError:
            pass

    amount_min = args.get("amount_min", type=float)
    if amount_min is not None:
        query = query.filter(Transaction.amount >= amount_min)

    amount_max = args.get("amount_max", type=float)
    if amount_max is not None:
        query = query.filter(Transaction.amount <= amount_max)

    month = args.get("month", type=int)
    if month:
        query = query.filter(extract("month", Transaction.date) == month)

    year = args.get("year", type=int)
    if year:
        query = query.filter(extract("year", Transaction.date) == year)

    sort_by = args.get("sort_by", "date_desc")
    sort_map = {
        "date_desc": Transaction.date.desc(),
        "date_asc": Transaction.date.asc(),
        "amount_desc": Transaction.amount.desc(),
        "amount_asc": Transaction.amount.asc(),
    }
    query = query.order_by(sort_map.get(sort_by, Transaction.date.desc()), Transaction.id.desc())
    return query


@transactions_bp.route("/")
@login_required
def list_transactions():
    filter_form = TransactionFilterForm(request.args, meta={"csrf": False})
    filter_form.category_id.choices = [(0, "All Categories")] + [
        (c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).order_by(Category.name)
    ]

    query = Transaction.query.filter_by(user_id=current_user.id)
    query = _apply_filters(query, request.args)

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["TRANSACTIONS_PER_PAGE"]
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "transactions/list.html",
        transactions=pagination.items,
        pagination=pagination,
        filter_form=filter_form,
    )


@transactions_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    form = TransactionForm()
    _populate_category_choices(form)
    if request.method == "GET":
        requested_type = request.args.get("type")
        if requested_type in ("income", "expense"):
            form.type.data = requested_type
        if not form.date.data:
            form.date.data = datetime.utcnow().date()

    if form.validate_on_submit():
        try:
            has_receipt = form.receipt.data and getattr(form.receipt.data, "filename", "")
            receipt_filename = save_receipt(form.receipt.data) if has_receipt else None
            tx = Transaction(
                user_id=current_user.id,
                category_id=form.category_id.data,
                type=form.type.data,
                amount=form.amount.data,
                date=form.date.data,
                payment_method=form.payment_method.data,
                notes=form.notes.data,
                receipt_image=receipt_filename,
            )
            db.session.add(tx)
            db.session.commit()
            flash("Transaction added successfully!", "success")
            return redirect(url_for("transactions.list_transactions"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            db.session.rollback()
            flash("Could not save transaction. Please try again.", "danger")
    elif request.method == "POST":
        # Repopulate categories since validation failed and page will re-render
        _populate_category_choices(form, tx_type=form.type.data)

    return render_template("transactions/form.html", form=form, mode="add")


@transactions_bp.route("/edit/<int:tx_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=current_user.id).first_or_404()
    form = TransactionForm(obj=tx)
    _populate_category_choices(form, tx_type=request.form.get("type") or tx.type)

    if request.method == "GET":
        form.category_id.data = tx.category_id

    if form.validate_on_submit():
        try:
            if form.receipt.data and getattr(form.receipt.data, "filename", ""):
                delete_receipt(tx.receipt_image)
                tx.receipt_image = save_receipt(form.receipt.data)

            tx.category_id = form.category_id.data
            tx.type = form.type.data
            tx.amount = form.amount.data
            tx.date = form.date.data
            tx.payment_method = form.payment_method.data
            tx.notes = form.notes.data
            db.session.commit()
            flash("Transaction updated successfully!", "success")
            return redirect(url_for("transactions.list_transactions"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            db.session.rollback()
            flash("Could not update transaction. Please try again.", "danger")

    return render_template("transactions/form.html", form=form, mode="edit", transaction=tx)


@transactions_bp.route("/delete/<int:tx_id>", methods=["POST"])
@login_required
def delete_transaction(tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=current_user.id).first_or_404()
    try:
        delete_receipt(tx.receipt_image)
        db.session.delete(tx)
        db.session.commit()
        flash("Transaction deleted.", "success")
    except Exception:
        db.session.rollback()
        flash("Could not delete transaction.", "danger")
    return redirect(url_for("transactions.list_transactions"))


@transactions_bp.route("/view/<int:tx_id>")
@login_required
def view_transaction(tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=current_user.id).first_or_404()
    return render_template("transactions/view.html", transaction=tx)


@transactions_bp.route("/export/csv")
@login_required
def export_csv():
    query = Transaction.query.filter_by(user_id=current_user.id)
    query = _apply_filters(query, request.args)
    transactions = query.all()
    csv_file = export_transactions_csv(transactions)
    return send_file(
        csv_file,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"transactions_{datetime.utcnow().strftime('%Y%m%d')}.csv",
    )
