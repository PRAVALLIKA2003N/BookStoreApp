# NORMALIZATION.md — Bookstore Database Normalization Report

## Overview

This report documents the normalization process applied to the Bookstore database (Users, Books, Orders, Order_items)**3rd Normal Form (3NF)** schema.

---

## 1. Original Schema (Starting Point)

The database was designed with four tables:

```
Users(user_id, name, email, created_at, updated_at, status)
Books(book_id, title, price, published_date, created_at, status)
Orders(order_id, user_id, order_date, created_at, status)
Order_items(item_id, order_id, book_id, quantity, created_at, status, total_price)
```

---

## 2. Original Functional Dependencies

### Users
| Determinant | Dependent Attributes |
|---|---|
| user_id → | name, email, created_at, updated_at, status |
| email → | user_id, name, created_at, updated_at, status *(email is a candidate key)* |

### Books
| Determinant | Dependent Attributes |
|---|---|
| book_id → | title, price, published_date, created_at, status |

### Orders
| Determinant | Dependent Attributes |
|---|---|
| order_id → | user_id, order_date, created_at, status |
| user_id → | *(partial — user info lives in Users table)* |

### Order_items
| Determinant | Dependent Attributes |
|---|---|
| item_id → | order_id, book_id, quantity, created_at, status, total_price |
| (order_id, book_id) → | quantity, total_price *(composite candidate key)* |
| book_id → | price *(transitive — price lives in Books, but total_price = quantity × price is derived here)* |

---

## 3. First Normal Form (1NF) Check

**Definition:** All attributes must be atomic (no repeating groups, no multi-valued columns).

| Table | 1NF Status | Notes |
|---|---|---|
| Users | ✅ Pass | All columns are atomic single values |
| Books | ✅ Pass | All columns are atomic single values |
| Orders | ✅ Pass | All columns are atomic single values |
| Order_items | ✅ Pass | All columns are atomic; each row represents one item |

**Result: All tables already satisfy 1NF.** No restructuring required at this stage.

---

## 4. Second Normal Form (2NF) Check

**Definition:** Must be in 1NF AND every non-key attribute must be **fully functionally dependent** on the *entire* primary key (no partial dependencies). Partial dependencies only arise when the primary key is composite.

### Tables with single-column primary keys (Users, Books, Orders)
No partial dependencies are possible. ✅ Pass automatically.

### Order_items — Composite Candidate Key Analysis

`Order_items` has `item_id` as the surrogate PK. However, `(order_id, book_id)` is a natural composite candidate key.

| Non-key Attribute | Depends on full (order_id, book_id)? | Issue? |
|---|---|---|
| quantity | ✅ Yes — quantity per specific order+book | None |
| total_price | ⚠️ Partially derived from book_id → price | Derived value |
| created_at | ✅ Yes — timestamp of this line item | None |
| status | ✅ Yes — status of this line item | None |

**`total_price` is a computed/derived column** (`quantity × Books.price`). It does not represent a true partial dependency but is a **derived attribute** that could cause **update anomalies** (if a book's price changes, existing `total_price` values become stale).

**2NF Resolution:** `total_price` should be treated as a **calculated virtual value**, not a stored column. It will be computed via application logic or a SQL view. We remove it from the base table to eliminate the anomaly.

**Result: All tables satisfy 2NF** after removing the derived `total_price` column from `Order_items`.

---

## 5. Third Normal Form (3NF) Check

**Definition:** Must be in 2NF AND every non-key attribute must depend **directly on the primary key** — no transitive dependencies (non-key → non-key → PK).

### Users
| Dependency Chain | Transitive? |
|---|---|
| user_id → name | ✅ Direct |
| user_id → email | ✅ Direct |
| user_id → created_at | ✅ Direct |
| user_id → updated_at | ✅ Direct |
| user_id → status | ✅ Direct |

No transitive dependencies. ✅ **Users is in 3NF.**

### Books
| Dependency Chain | Transitive? |
|---|---|
| book_id → title | ✅ Direct |
| book_id → price | ✅ Direct |
| book_id → published_date | ✅ Direct |
| book_id → created_at | ✅ Direct |
| book_id → status | ✅ Direct |

No transitive dependencies. ✅ **Books is in 3NF.**

### Orders
| Dependency Chain | Transitive? |
|---|---|
| order_id → user_id | ✅ Direct (FK reference) |
| order_id → order_date | ✅ Direct |
| order_id → created_at | ✅ Direct |
| order_id → status | ✅ Direct |

No transitive dependencies. ✅ **Orders is in 3NF.**

### Order_items
| Dependency Chain | Transitive? |
|---|---|
| item_id → order_id | ✅ Direct (FK reference) |
| item_id → book_id | ✅ Direct (FK reference) |
| item_id → quantity | ✅ Direct |
| item_id → created_at | ✅ Direct |
| item_id → status | ✅ Direct |
|item_id → total_price | ❌ Removed (derived from book_id → price) |

After removing `total_price`, no transitive dependencies remain. ✅ **Order_items is in 3NF.**

---

## 6. Anomaly Identification

### Update Anomaly
**Problem:** `total_price` was stored directly in `Order_items`. If the price of a book in the `Books` table is updated, all previously calculated `total_price` values in `Order_items` become incorrect without a manual cascading update.

Remove `total_price` as a stored column. Compute it dynamically: `quantity * Books.price` via a JOIN query or a database VIEW.

### Insertion Anomaly
**Problem (hypothetical):** If a user's information (e.g., address or status) were embedded directly in `Orders` instead of referenced by FK, you could not record an order without duplicating user data, or insert user data without an associated order.

User data is properly separated into the `Users` table and referenced via `user_id` foreign key in `Orders`. ✅

### Deletion Anomaly
**Problem (hypothetical):** If book details (title, price) were stored directly in `Order_items` instead of referenced by FK, deleting all order items for a book would destroy the book's data entirely.

 Book data is properly separated into the `Books` table and referenced via `book_id` FK in `Order_items`. ✅

---

## 7. Decomposition Steps

### Step 1 — Remove derived column from Order_items

**Before:**
```sql
Order_items(item_id, order_id, book_id, quantity, created_at, status, total_price)
```

**After:**
```sql
Order_items(item_id, order_id, book_id, quantity, created_at, status)
```

`total_price` is now computed on-the-fly via SQL:
```sql
SELECT oi.item_id, oi.quantity, b.price, (oi.quantity * b.price) AS total_price
FROM Order_items oi
JOIN Books b ON oi.book_id = b.book_id;
```

### Step 2 — Verify all foreign key constraints are explicit

All relationships are enforced with explicit FK constraints in the schema to ensure referential integrity (no orphan orders or order items).

No further decomposition was required — the original design was already well-structured with proper table separation.

---

## 8. Final Relational Schema (3NF)

This is the schema the Python Flask application uses:

```
Users
------
user_id     INT          PRIMARY KEY
name        VARCHAR(100) NOT NULL
email       VARCHAR(100) NOT NULL UNIQUE
created_at  DATE         NOT NULL
updated_at  DATE
status      VARCHAR(50)  DEFAULT 'active'

Books
------
book_id         INT           PRIMARY KEY
title           VARCHAR(100)  NOT NULL
price           DECIMAL(10,2) NOT NULL CHECK (price >= 0)
published_date  DATE
created_at      DATE          NOT NULL
status          VARCHAR(50)   DEFAULT 'available'

Orders
------
order_id    INT         PRIMARY KEY
user_id     INT         NOT NULL  REFERENCES Users(user_id)
order_date  DATE        NOT NULL
created_at  DATE        NOT NULL
status      VARCHAR(50) DEFAULT 'pending'

Order_items
------
item_id     INT          PRIMARY KEY
order_id    INT          NOT NULL  REFERENCES Orders(order_id)
book_id     INT          NOT NULL  REFERENCES Books(book_id)
quantity    INT          NOT NULL  CHECK (quantity > 0)
created_at  DATE         NOT NULL
status      VARCHAR(50)  DEFAULT 'ok'
-- total_price is COMPUTED: quantity * Books.price (NOT stored)
```

### Entity-Relationship Summary

```
Users ──< Orders ──< Order_items >── Books
(1)       (Many)     (Many)           (1)
```

- **Users → Orders:** One-to-Many (one user can place many orders)
- **Orders → Order_items:** One-to-Many (one order can contain many line items)
- **Books → Order_items:** One-to-Many (one book can appear in many order items)
- **Orders ↔ Books via Order_items:** Many-to-Many (resolved through junction table)

---

## 9. Summary

| Normal Form | Status | Action Taken |
|---|---|---|
| 1NF | ✅ Already satisfied | No changes needed |
| 2NF | ✅ Achieved | Removed derived `total_price` column |
| 3NF | ✅ Achieved | Confirmed no transitive dependencies remain |

