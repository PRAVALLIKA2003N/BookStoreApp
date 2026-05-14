"""
CS665 Project 3 — Bookstore Full-Stack Application
Flask + SQLite + SQLAlchemy + Jinja2
"""

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
from datetime import date
import os

# ─────────────────────────────────────────────
# App & DB Setup
# ─────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "bookstore-dev-secret-2024")

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(basedir, "instance", "bookstore.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ─────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────

class User(db.Model):
    __tablename__ = "Users"
    user_id    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.Date, nullable=False, default=date.today)
    updated_at = db.Column(db.Date, nullable=False, default=date.today, onupdate=date.today)
    status     = db.Column(db.String(50), nullable=False, default="active")
    orders     = db.relationship("Order", backref="user", lazy=True)


class Book(db.Model):
    __tablename__ = "Books"
    book_id        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title          = db.Column(db.String(200), nullable=False)
    author         = db.Column(db.String(150), nullable=False, default="Unknown")
    price          = db.Column(db.Numeric(10, 2), nullable=False)
    published_date = db.Column(db.Date)
    created_at     = db.Column(db.Date, nullable=False, default=date.today)
    status         = db.Column(db.String(50), nullable=False, default="available")
    order_items    = db.relationship("OrderItem", backref="book", lazy=True)


class Order(db.Model):
    __tablename__ = "Orders"
    order_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("Users.user_id"), nullable=False)
    order_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.Date, nullable=False, default=date.today)
    status     = db.Column(db.String(50), nullable=False, default="pending")
    items      = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")


class OrderItem(db.Model):
    __tablename__ = "Order_Items"
    item_id    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id   = db.Column(db.Integer, db.ForeignKey("Orders.order_id"), nullable=False)
    book_id    = db.Column(db.Integer, db.ForeignKey("Books.book_id"), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.Date, nullable=False, default=date.today)
    status     = db.Column(db.String(50), nullable=False, default="ok")

    @property
    def total_price(self):
        """Computed per 3NF: quantity × book.price (not stored)."""
        return float(self.quantity) * float(self.book.price)


# ─────────────────────────────────────────────
# Validation Helpers
# ─────────────────────────────────────────────

def validate_user(name, email, status):
    errors = []
    if not name or not name.strip():
        errors.append("Name is required.")
    if not email or not email.strip():
        errors.append("Email is required.")
    elif "@" not in email:
        errors.append("Email must be a valid address.")
    if status not in ("active", "inactive"):
        errors.append("Status must be 'active' or 'inactive'.")
    return errors


def validate_book(title, author, price, status):
    errors = []
    if not title or not title.strip():
        errors.append("Title is required.")
    if not author or not author.strip():
        errors.append("Author is required.")
    try:
        p = float(price)
        if p < 0:
            errors.append("Price cannot be negative.")
    except (TypeError, ValueError):
        errors.append("Price must be a valid number.")
    if status not in ("available", "unavailable"):
        errors.append("Status must be 'available' or 'unavailable'.")
    return errors


def validate_order_item(book_id, quantity):
    errors = []
    if not book_id:
        errors.append("A book must be selected.")
    try:
        q = int(quantity)
        if q <= 0:
            errors.append("Quantity must be a positive integer.")
    except (TypeError, ValueError):
        errors.append("Quantity must be a valid integer.")
    return errors


# ─────────────────────────────────────────────
# Routes — Dashboard
# ─────────────────────────────────────────────

@app.route("/")
def dashboard():
    total_users  = db.session.query(func.count(User.user_id)).scalar()
    total_books  = db.session.query(func.count(Book.book_id)).scalar()
    total_orders = db.session.query(func.count(Order.order_id)).scalar()
    total_items  = db.session.query(func.count(OrderItem.item_id)).scalar()

    avg_price = db.session.query(func.avg(Book.price)).scalar()
    avg_price = round(float(avg_price), 2) if avg_price else 0.0

    # Revenue: SUM(quantity * price) via JOIN
    revenue_rows = (
        db.session.query(OrderItem.quantity, Book.price)
        .join(Book, OrderItem.book_id == Book.book_id)
        .all()
    )
    total_revenue = sum(float(r.quantity) * float(r.price) for r in revenue_rows)

    # Top 5 customers by order count
    top_customers = (
        db.session.query(User.name, func.count(Order.order_id).label("num_orders"))
        .join(Order, User.user_id == Order.user_id)
        .group_by(User.user_id)
        .order_by(func.count(Order.order_id).desc())
        .limit(5)
        .all()
    )

    # Orders by status
    status_counts = (
        db.session.query(Order.status, func.count(Order.order_id).label("cnt"))
        .group_by(Order.status)
        .all()
    )

    # Recent orders
    recent_orders = (
        Order.query.order_by(Order.order_date.desc()).limit(5).all()
    )

    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_books=total_books,
        total_orders=total_orders,
        total_items=total_items,
        avg_price=avg_price,
        total_revenue=total_revenue,
        top_customers=top_customers,
        status_counts=status_counts,
        recent_orders=recent_orders,
    )


# ─────────────────────────────────────────────
# Routes — Users CRUD
# ─────────────────────────────────────────────

@app.route("/users")
def users_list():
    users = User.query.order_by(User.user_id).all()
    return render_template("users/list.html", users=users)


@app.route("/users/new", methods=["GET", "POST"])
def users_new():
    if request.method == "POST":
        name   = request.form.get("name", "").strip()
        email  = request.form.get("email", "").strip()
        status = request.form.get("status", "active")
        errors = validate_user(name, email, status)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("users/form.html", user=None, action="Create")
        # Check duplicate email
        if User.query.filter_by(email=email).first():
            flash("That email is already registered.", "danger")
            return render_template("users/form.html", user=None, action="Create")
        user = User(name=name, email=email, status=status)
        db.session.add(user)
        db.session.commit()
        flash(f"User '{name}' created successfully.", "success")
        return redirect(url_for("users_list"))
    return render_template("users/form.html", user=None, action="Create")


@app.route("/users/<int:uid>/edit", methods=["GET", "POST"])
def users_edit(uid):
    user = User.query.get_or_404(uid)
    if request.method == "POST":
        name   = request.form.get("name", "").strip()
        email  = request.form.get("email", "").strip()
        status = request.form.get("status", "active")
        errors = validate_user(name, email, status)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("users/form.html", user=user, action="Update")
        # Check duplicate email (exclude current)
        dup = User.query.filter(User.email == email, User.user_id != uid).first()
        if dup:
            flash("That email is already used by another user.", "danger")
            return render_template("users/form.html", user=user, action="Update")
        user.name       = name
        user.email      = email
        user.status     = status
        user.updated_at = date.today()
        db.session.commit()
        flash(f"User '{name}' updated.", "success")
        return redirect(url_for("users_list"))
    return render_template("users/form.html", user=user, action="Update")


@app.route("/users/<int:uid>/delete", methods=["POST"])
def users_delete(uid):
    user = User.query.get_or_404(uid)
    if user.orders:
        flash("Cannot delete a user who has orders. Remove orders first.", "danger")
        return redirect(url_for("users_list"))
    db.session.delete(user)
    db.session.commit()
    flash("User deleted.", "success")
    return redirect(url_for("users_list"))


@app.route("/users/<int:uid>")
def users_detail(uid):
    user = User.query.get_or_404(uid)
    return render_template("users/detail.html", user=user)


# ─────────────────────────────────────────────
# Routes — Books CRUD
# ─────────────────────────────────────────────

@app.route("/books")
def books_list():
    books = Book.query.order_by(Book.book_id).all()
    return render_template("books/list.html", books=books)


@app.route("/books/new", methods=["GET", "POST"])
def books_new():
    if request.method == "POST":
        title  = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        price  = request.form.get("price", "")
        status = request.form.get("status", "available")
        pub    = request.form.get("published_date") or None
        errors = validate_book(title, author, price, status)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("books/form.html", book=None, action="Create")
        book = Book(title=title, author=author, price=float(price),
                    status=status, published_date=pub)
        db.session.add(book)
        db.session.commit()
        flash(f"Book '{title}' added.", "success")
        return redirect(url_for("books_list"))
    return render_template("books/form.html", book=None, action="Create")


@app.route("/books/<int:bid>/edit", methods=["GET", "POST"])
def books_edit(bid):
    book = Book.query.get_or_404(bid)
    if request.method == "POST":
        title  = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        price  = request.form.get("price", "")
        status = request.form.get("status", "available")
        pub    = request.form.get("published_date") or None
        errors = validate_book(title, author, price, status)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("books/form.html", book=book, action="Update")
        book.title          = title
        book.author         = author
        book.price          = float(price)
        book.status         = status
        book.published_date = pub
        db.session.commit()
        flash(f"Book '{title}' updated.", "success")
        return redirect(url_for("books_list"))
    return render_template("books/form.html", book=book, action="Update")


@app.route("/books/<int:bid>/delete", methods=["POST"])
def books_delete(bid):
    book = Book.query.get_or_404(bid)
    if book.order_items:
        flash("Cannot delete a book that appears in orders.", "danger")
        return redirect(url_for("books_list"))
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted.", "success")
    return redirect(url_for("books_list"))


# ─────────────────────────────────────────────
# Routes — Orders CRUD + Transaction Logic
# ─────────────────────────────────────────────

@app.route("/orders")
def orders_list():
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template("orders/list.html", orders=orders)


@app.route("/orders/new", methods=["GET", "POST"])
def orders_new():
    """
    Transaction Logic:
    Creating an order and its first item happens in a single atomic transaction.
    If the order item insert fails (bad data), the entire order is rolled back.
    """
    users = User.query.filter_by(status="active").order_by(User.name).all()
    books = Book.query.filter_by(status="available").order_by(Book.title).all()
    if request.method == "POST":
        user_id  = request.form.get("user_id")
        book_id  = request.form.get("book_id")
        quantity = request.form.get("quantity", "1")
        status   = request.form.get("status", "pending")

        if not user_id:
            flash("Please select a customer.", "danger")
            return render_template("orders/form.html", users=users, books=books)

        errors = validate_order_item(book_id, quantity)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("orders/form.html", users=users, books=books)

        # ── TRANSACTION: create Order + OrderItem atomically ──
        try:
            order = Order(user_id=int(user_id), status=status)
            db.session.add(order)
            db.session.flush()  # get order.order_id before commit

            item = OrderItem(
                order_id=order.order_id,
                book_id=int(book_id),
                quantity=int(quantity),
            )
            db.session.add(item)
            db.session.commit()
            flash(f"Order #{order.order_id} created with 1 item.", "success")
            return redirect(url_for("orders_detail", oid=order.order_id))
        except Exception as ex:
            db.session.rollback()
            flash(f"Transaction failed and was rolled back: {ex}", "danger")
            return render_template("orders/form.html", users=users, books=books)

    return render_template("orders/form.html", users=users, books=books)


@app.route("/orders/<int:oid>")
def orders_detail(oid):
    order = Order.query.get_or_404(oid)
    books = Book.query.filter_by(status="available").order_by(Book.title).all()
    return render_template("orders/detail.html", order=order, books=books)


@app.route("/orders/<int:oid>/status", methods=["POST"])
def orders_update_status(oid):
    order = Order.query.get_or_404(oid)
    new_status = request.form.get("status")
    if new_status not in ("pending", "completed", "cancelled"):
        flash("Invalid status.", "danger")
        return redirect(url_for("orders_detail", oid=oid))
    order.status = new_status
    db.session.commit()
    flash(f"Order #{oid} status updated to '{new_status}'.", "success")
    return redirect(url_for("orders_detail", oid=oid))


@app.route("/orders/<int:oid>/add_item", methods=["POST"])
def orders_add_item(oid):
    """Transaction: log the new item only if validation passes."""
    order   = Order.query.get_or_404(oid)
    book_id  = request.form.get("book_id")
    quantity = request.form.get("quantity", "1")
    errors   = validate_order_item(book_id, quantity)
    if errors:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("orders_detail", oid=oid))
    try:
        item = OrderItem(order_id=oid, book_id=int(book_id), quantity=int(quantity))
        db.session.add(item)
        db.session.commit()
        flash("Item added to order.", "success")
    except Exception as ex:
        db.session.rollback()
        flash(f"Could not add item: {ex}", "danger")
    return redirect(url_for("orders_detail", oid=oid))


@app.route("/orders/<int:oid>/remove_item/<int:iid>", methods=["POST"])
def orders_remove_item(oid, iid):
    item = OrderItem.query.get_or_404(iid)
    db.session.delete(item)
    db.session.commit()
    flash("Item removed.", "success")
    return redirect(url_for("orders_detail", oid=oid))


@app.route("/orders/<int:oid>/delete", methods=["POST"])
def orders_delete(oid):
    order = Order.query.get_or_404(oid)
    db.session.delete(order)
    db.session.commit()
    flash(f"Order #{oid} deleted.", "success")
    return redirect(url_for("orders_list"))


# ─────────────────────────────────────────────
# Init DB command
# ─────────────────────────────────────────────

def init_db():
    os.makedirs(os.path.join(basedir, "instance"), exist_ok=True)
    with app.app_context():
        db.create_all()
        # Seed only if empty
        if User.query.count() == 0:
            users = [
                User(name="Alice",   email="alice@mail.com",   created_at=date(2024,1,1), updated_at=date(2024,1,2), status="active"),
                User(name="Bob",     email="bob@mail.com",     created_at=date(2024,2,1), updated_at=date(2024,2,2), status="active"),
                User(name="Charlie", email="charlie@mail.com", created_at=date(2024,3,1), updated_at=date(2024,3,2), status="inactive"),
                User(name="David",   email="david@mail.com",   created_at=date(2024,4,1), updated_at=date(2024,4,2), status="active"),
                User(name="Eva",     email="eva@mail.com",     created_at=date(2024,5,1), updated_at=date(2024,5,2), status="active"),
            ]
            db.session.add_all(users)
            db.session.flush()

            books = [
                Book(title="SQL Basics",   author="Jane Smith",  price=20.00, published_date=date(2020,1,1), created_at=date(2020,1,5), status="available"),
                Book(title="Python Guide", author="John Doe",    price=25.00, published_date=date(2021,2,1), created_at=date(2021,2,5), status="available"),
                Book(title="ML Intro",     author="Sara Lee",    price=30.00, published_date=date(2022,3,1), created_at=date(2022,3,5), status="available"),
                Book(title="AI Advanced",  author="Tom Brown",   price=40.00, published_date=date(2023,4,1), created_at=date(2023,4,5), status="available"),
                Book(title="Data Science", author="Emily Clark", price=35.00, published_date=date(2023,5,1), created_at=date(2023,5,5), status="available"),
            ]
            db.session.add_all(books)
            db.session.flush()

            orders = [
                Order(user_id=users[0].user_id, order_date=date(2024,6,1), created_at=date(2024,6,1), status="completed"),
                Order(user_id=users[1].user_id, order_date=date(2024,6,2), created_at=date(2024,6,2), status="completed"),
                Order(user_id=users[2].user_id, order_date=date(2024,6,3), created_at=date(2024,6,3), status="pending"),
                Order(user_id=users[0].user_id, order_date=date(2024,6,4), created_at=date(2024,6,4), status="completed"),
                Order(user_id=users[1].user_id, order_date=date(2024,6,5), created_at=date(2024,6,5), status="pending"),
            ]
            db.session.add_all(orders)
            db.session.flush()

            items = [
                OrderItem(order_id=orders[0].order_id, book_id=books[0].book_id, quantity=2, created_at=date(2024,6,1)),
                OrderItem(order_id=orders[1].order_id, book_id=books[1].book_id, quantity=1, created_at=date(2024,6,2)),
                OrderItem(order_id=orders[2].order_id, book_id=books[2].book_id, quantity=3, created_at=date(2024,6,3)),
                OrderItem(order_id=orders[3].order_id, book_id=books[3].book_id, quantity=1, created_at=date(2024,6,4)),
                OrderItem(order_id=orders[4].order_id, book_id=books[4].book_id, quantity=2, created_at=date(2024,6,5)),
            ]
            db.session.add_all(items)
            db.session.commit()
            print("✅ Database seeded.")
        else:
            print("✅ Database already seeded.")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
