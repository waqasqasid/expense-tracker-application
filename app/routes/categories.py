"""Category management: view, create, edit, delete custom categories."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models.category import Category
from app.forms.transaction_forms import CategoryForm

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/")
@login_required
def list_categories():
    income_categories = (
        Category.query.filter_by(user_id=current_user.id, type="income").order_by(Category.name).all()
    )
    expense_categories = (
        Category.query.filter_by(user_id=current_user.id, type="expense").order_by(Category.name).all()
    )
    return render_template(
        "categories/list.html",
        income_categories=income_categories,
        expense_categories=expense_categories,
    )


@categories_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        existing = Category.query.filter_by(
            user_id=current_user.id, name=form.name.data.strip(), type=form.type.data
        ).first()
        if existing:
            flash("You already have a category with that name and type.", "warning")
        else:
            category = Category(
                name=form.name.data.strip(),
                type=form.type.data,
                icon=form.icon.data or "bi-tag",
                is_default=False,
                user_id=current_user.id,
            )
            db.session.add(category)
            db.session.commit()
            flash("Category created successfully!", "success")
            return redirect(url_for("categories.list_categories"))

    return render_template("categories/form.html", form=form, mode="add")


@categories_bp.route("/edit/<int:cat_id>", methods=["GET", "POST"])
@login_required
def edit_category(cat_id):
    category = Category.query.filter_by(id=cat_id, user_id=current_user.id).first_or_404()
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data.strip()
        category.type = form.type.data
        category.icon = form.icon.data or "bi-tag"
        db.session.commit()
        flash("Category updated successfully!", "success")
        return redirect(url_for("categories.list_categories"))
    return render_template("categories/form.html", form=form, mode="edit", category=category)


@categories_bp.route("/delete/<int:cat_id>", methods=["POST"])
@login_required
def delete_category(cat_id):
    category = Category.query.filter_by(id=cat_id, user_id=current_user.id).first_or_404()
    if category.transactions.count() > 0:
        flash(
            "Cannot delete a category that has transactions. Reassign or delete those transactions first.",
            "danger",
        )
    else:
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted.", "success")
    return redirect(url_for("categories.list_categories"))
