# AI Assistance Log — CS665 Project 3
Entry 1

Tool: Claude

Prompt:

"I need complete instructions for Part 2, including clear steps and explanations."

AI Output Summary:
The AI generated the overall project requirements, implementation steps, and guidance needed to complete the project.

Entry 2

Tool: Claude

Prompt:

"What setup and software do I need for this project?"

AI Output Summary:
The AI provided the required software, environment setup instructions, and recommended versions for the tools needed for development.

Entry 3

Tool: Claude (Anthropic, claude.ai)

Prompt:

"I have a Flask e-commerce project with 4 tables: Users, Books, Orders, Order_Items. Generate a SQLAlchemy models file and Flask app with CRUD routes for all four entities."

AI Output Summary:
The AI generated a database.py file with SQLAlchemy model classes using db.relationship() for foreign key relationships, along with an app.py containing CRUD routes for listing, adding, editing, and deleting records.

My Modifications:

Added server-side validation logic (empty string validation, negative price validation, email format checks, duplicate email checks)
Updated column names to match my database schema
Added transactional order creation using db.session.flush() and db.session.rollback() for error handling
Modified relationships for consistency across models
Removed unused auto-generated testing code that did not match the project structure
Entry 4

Tool: Claude (Anthropic, claude.ai)

Prompt:

"Generate a Bootstrap 5 Jinja2 base template with a dark navbar and flash message support for a Flask app with routes: dashboard, customers, sellers, products, orders."

AI Output Summary:
The AI generated a base.html template with a Bootstrap dark navigation bar, responsive mobile menu, and flash message support using get_flashed_messages(with_categories=True).

My Modifications:

Added active navigation highlighting using request.endpoint
Added Bootstrap Icons CDN integration
Updated the layout container for improved responsiveness
Added a {% block scripts %} section for page-specific JavaScript support
Entry 5

Tool: Claude (Anthropic, claude.ai)

Prompt:

"Write a NORMALIZATION.md for a database schema with tables Users, Books, Orders, Order_Items. Identify functional dependencies, anomalies, and show 3NF analysis."

AI Output Summary:
The AI generated a normalization report covering 1NF, 2NF, and 3NF analysis along with dependency explanations and anomaly discussions.

My Modifications:

Updated anomaly explanations to better match my database schema
Added justification for the derived total_price calculation
Revised the schema description to align with the actual implementation
Added clarification about the many-to-many relationship between Orders and Products through Order_Items
Entry 6

Tool: Claude (Anthropic, claude.ai)

Prompt:

"Write a dashboard Flask route and Jinja2 template that shows aggregate stats:  Users, Books, Orders, Order_Items.
AI Output Summary:
The AI generated a dashboard route using SQLAlchemy aggregate functions (func.count, func.sum, func.avg) and created a Bootstrap dashboard layout with statistic cards.

My Modifications:

Corrected the revenue calculation query to match the project schema
Added null-safe handling for SUM and AVG calculations
Added color-coded status badges for order statuses
Improved the dashboard layout using a responsive grid structure
Entry 7

Tool: Claude

Prompt:

"Can you explain how to start using Git and create commits incrementally?"

AI Output Summary:
The AI provided step-by-step guidance for initializing a Git repository, creating commits, and managing version control incrementally throughout the project.

All AI-generated code and documentation were reviewed, tested, and modified before being included in this repository.

Entry 8

Prompt " Git Setup"

AI Output Summary:

python --version
cd C:\Users\prava\Downloads\bookstore
python -m venv venv
venv\Scripts\activate
pip install flask
python -c "from app import init_db; init_db()"
python app.py
Running on http://127.0.0.1:5000