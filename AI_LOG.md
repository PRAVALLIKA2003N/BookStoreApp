# AI Assistance Log — CS665 Project 3

This file documents all uses of Generative AI during the development of this project, per the course's AI disclosure policy.

---

## Entry 1

**Tool:** Claude (Anthropic — claude.ai)

**Prompt:**
> "Use this two files [CS665_Project_3.pdf and Database.docx] and generate Part A normalization.md file and Part B completely with all html and css files and everything that is specified in the pdf file."

**AI Output Summary:**
The AI generated:
- `NORMALIZATION.md` — full normalization audit reducing the schema to 3NF, including functional dependencies, anomaly analysis, decomposition steps, and final relational schema.
- `schema.sql` — 3NF-compliant SQLite DDL with seed data.
- `app.py` — Flask application with SQLAlchemy models, full CRUD routes for Users, Books, and Orders, server-side validation, and transaction logic.
- HTML templates (`base.html`, `dashboard.html`, `users/list.html`, `users/form.html`, `users/detail.html`, `books/list.html`, `books/form.html`, `orders/list.html`, `orders/form.html`, `orders/detail.html`) using Bootstrap 5 and Jinja2.
- `static/css/style.css` — custom styling for stat cards, status badges, and book cards.
- `static/js/main.js` — confirm-delete dialogs and UX helpers.
- `requirements.txt`, `.gitignore`, `README.md`, `AI_LOG.md`.

**My Modifications & Verification:**
- Reviewed all functional dependencies listed in `NORMALIZATION.md` against the original `Database.docx` DDL to confirm accuracy.
- Verified that `total_price` was correctly identified as a 3NF violation (derived from `quantity × price`) and removed from the schema.
- Confirmed the `author` column was a practical addition missing from the original schema and added it to seed data.
- Checked Flask routes to confirm server-side validation rejects negative prices, empty strings, and invalid quantities before any DB write.
- Traced the transaction logic in `orders_new()` and `orders_add_item()` to verify `db.session.flush()` → `db.session.commit()` / `db.session.rollback()` pattern is correct.
- Tested the application locally to confirm all CRUD operations and the dashboard aggregate queries work correctly.
- Adjusted Bootstrap class usage and badge color scheme to match the existing status values (`ok`, `active`, `inactive`, `pending`, `completed`, `cancelled`).

---

*No AI output was used without manual review and verification against the actual database schema and project requirements.*
