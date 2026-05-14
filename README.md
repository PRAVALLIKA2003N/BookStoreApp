# 📚 CS665 Bookstore — Project 3

A full-stack bookstore management application built with **Python 3 + Flask + SQLAlchemy + SQLite + Bootstrap 5**.

---

## Project Description

This application allows bookstore staff to manage customers, a book catalog, and customer orders. It demonstrates:

- **Multi-table CRUD** across Users, Books, Orders, and Order_Items
- **One-to-Many relationships** (User → Orders, Order → Items)
- **SQL transaction logic** (creating an order + first item atomically)
- **Server-side data validation** (no negative prices, empty fields, or zero quantities)
- **Summary dashboard** with COUNT, SUM, and AVG aggregates

**Who is it for?** Bookstore managers who need a clean, browser-based interface for day-to-day inventory and order tracking.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Backend | Flask 3.0 |
| ORM | Flask-SQLAlchemy 3.1 / SQLAlchemy 2.0 |
| Database | SQLite (via SQLAlchemy) |
| Frontend | HTML5, CSS3, Bootstrap 5.3, Jinja2 |
| Version Control | Git |

---

## Installation Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd bookstore_app
```

### 2. Create and activate a virtual environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Database Setup

The application uses SQLite. The database is created and seeded automatically when you first run the app. No separate SQL step is required.

If you prefer to inspect the schema manually, the `schema.sql` file contains the final 3NF DDL and seed data compatible with SQLite:

```bash
sqlite3 instance/bookstore.db < schema.sql
```

---

## Usage

### Launch the development server

```bash
python app.py
```

Open your browser and navigate to: **http://127.0.0.1:5000**

### Main Features

| Page | URL | Description |
|---|---|---|
| Dashboard | `/` | Aggregate stats: total users, books, orders, revenue, avg price, top customers |
| Users | `/users` | List, create, edit, delete customers; view all orders per user |
| Books | `/books` | Manage the book catalog with pricing |
| Orders | `/orders` | View and manage all orders |
| New Order | `/orders/new` | Atomic transaction: creates order + first item together |
| Order Detail | `/orders/<id>` | View items, update status, add/remove items |

---

## Key Design Decisions

### 3rd Normal Form
`total_price` was **removed** from `Order_Items` because it is a derived column (`quantity × Books.price`), creating a transitive dependency. It is computed on-the-fly in queries and the `total_price` property on the `OrderItem` model. See `NORMALIZATION.md` for the full audit.

### Transaction Logic
Creating a new order (`POST /orders/new`) wraps both the `INSERT INTO Orders` and `INSERT INTO Order_Items` in a single SQLAlchemy transaction. If either fails, `db.session.rollback()` is called and an error is shown. The same pattern applies when adding items to an existing order.

### Server-side Validation
All form submissions are validated before any database write:
- Name and email fields cannot be empty; email must contain `@`
- Book prices must be ≥ 0
- Order item quantities must be positive integers
- Duplicate emails are rejected

---

## Repository Structure

```
bookstore_app/
├── app.py                  # Flask app, models, routes, validation
├── schema.sql              # 3NF DDL + seed data (SQLite)
├── requirements.txt
├── .gitignore
├── README.md
├── NORMALIZATION.md        # Part I — 3NF audit report
├── AI_LOG.md               # AI disclosure
├── instance/               # SQLite DB (git-ignored)
├── static/
│   ├── css/style.css
│   └── js/main.js
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── users/
    │   ├── list.html
    │   ├── form.html
    │   └── detail.html
    ├── books/
    │   ├── list.html
    │   └── form.html
    └── orders/
        ├── list.html
        ├── form.html
        └── detail.html
```

---

## Git Commit History Guidance

Maintain at least 5 incremental commits, for example:

1. `init: project structure and Flask app skeleton`
2. `feat: add SQLAlchemy models and database schema`
3. `feat: implement Users CRUD with validation`
4. `feat: implement Books CRUD`
5. `feat: implement Orders with transaction logic`
6. `feat: dashboard with aggregate SQL queries`
7. `style: Bootstrap 5 templates and custom CSS`
8. `docs: add NORMALIZATION.md, README, AI_LOG`

---

## License

Academic project — CS665, 2024.
