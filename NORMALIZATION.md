Adding # Normalization Report — Bookstore Database

## Overview

This document audits the original bookstore database schema (Users, Books, Orders, Order_Items) and reduces it to **Third Normal Form (3NF)**. It covers original functional dependencies, anomaly identification, decomposition steps, and the final relational schema.

---

## 1. Original Schema

The starting schema (from the DDL in `Database.docx`)

```
Users(user_id, name, email, created_at, updated_at, status)
Books(book_id, title, price, published_date, created_at, status)
Orders(order_id, user_id, order_date, created_at, status)
Order_Items(item_id, order_id, book_id, quantity, created_at, status, total_price)
```

> **Note:** `total_price` was added via `ALTER TABLE` in the original DML as a derived column (`quantity * price`).

---

## 2. Original Functional Dependencies

### Users Table
| Determinant | Dependent Attributes |
|---|---|
| user_id → | name, email, created_at, updated_at, status |
| email → | user_id, name, created_at, updated_at, status (email is unique) |

### Books Table
| Determinant | Dependent Attributes |
|---|---|
| book_id → | title, price, published_date, created_at, status |

### Orders Table
| Determinant | Dependent Attributes |
|---|---|
| order_id → | user_id, order_date, created_at, status |
| user_id → | (partial — user attributes live in Users table) |

### Order_Items Table
| Determinant | Dependent Attributes |
|---|---|
| item_id → | order_id, book_id, quantity, created_at, status, total_price |
| (order_id, book_id) → | quantity, total_price (composite candidate key) |
| book_id → | price (transitive — price lives in Books, but total_price depends on it) |
| total_price → | quantity × price (derived/computed, not independently determined) |

---

## 3. Normal Form Analysis

### First Normal Form (1NF)
**All tables satisfy 1NF.**
- Every column holds atomic (single) values.
- Each row is uniquely identified by a primary key.
- No repeating groups or arrays exist.

✅ Users — atomic columns, PK = user_id  
✅ Books — atomic columns, PK = book_id  
✅ Orders — atomic columns, PK = order_id  
✅ Order_Items — atomic columns, PK = item_id  

---

### Second Normal Form (2NF)
**2NF requires 1NF + no partial dependencies (every non-key attribute must depend on the *whole* primary key).**

Since `Users`, `Books`, and `Orders` all have **single-column** primary keys, partial dependencies are impossible in those tables — they automatically satisfy 2NF.

For `Order_Items`, the natural composite key is `(order_id, book_id)`, but the table uses a surrogate `item_id` as PK. Under `item_id` as PK, all columns are fully dependent on `item_id`, so no partial dependency exists formally. However:

- `total_price` is derived from `quantity × Books.price` — this is a **derived attribute**, which is a 2NF/3NF concern addressed below.

✅ All tables satisfy 2NF.

---

### Third Normal Form (3NF)
**3NF requires 2NF + no transitive dependencies (no non-key attribute depends on another non-key attribute).**

#### Violation Found: `Order_Items.total_price`

`total_price` is computed as `quantity × price`, where `price` comes from the `Books` table.

- `total_price` depends on `quantity` (non-key) and `book_id → price` (via Books).
- This is a **transitive dependency**: `item_id → book_id → price → total_price`.
- Storing `total_price` also introduces **redundancy**: if a book's price changes, every `Order_Item` row referencing that book needs updating — an **update anomaly**.

**Resolution:** Remove `total_price` from `Order_Items`. Compute it on-the-fly in application queries using `quantity * Books.price`.

#### Other Observations

| Table | Potential Issue | Assessment |
|---|---|---|
| Users | `updated_at` is metadata, not derived | ✅ Fine — it records the last modification timestamp |
| Books | `created_at` + `status` are independent | ✅ Fine — no transitive dependency |
| Orders | `status` is independent of `user_id` | ✅ Fine |
| Order_Items | `total_price = quantity × price` | ❌ **Transitive/derived — remove** |

---

## 4. Anomaly Identification

### Update Anomaly
- **Problem:** If `Books.price` changes (e.g., a sale), all existing `Order_Items.total_price` values become stale and incorrect.
- **Impact:** Every row in `Order_Items` referencing that book must be manually updated.
- **Fix:** Remove `total_price`; compute dynamically via JOIN.

### Insertion Anomaly
- **Problem:** A new `Order_Item` cannot have `total_price` set correctly until `Books.price` is known, creating a chicken-and-egg dependency.
- **Fix:** Removing the derived column eliminates this issue entirely.

### Deletion Anomaly
- **Problem:** Deleting a Book that is referenced by Order_Items would cascade and lose historical order data (or be blocked by FK constraints).
- **Fix:** The FK constraint already handles this; no schema change needed beyond the derived column removal.

---

## 5. Decomposition Steps

### Step 1 — Identify the violation

`Order_Items.total_price` is a derived attribute:
```
total_price = quantity × price   (price from Books table)
```
This creates a transitive dependency: `item_id → book_id → price → total_price`.

### Step 2 — Remove the derived attribute

**Before (violates 3NF):**
```sql
CREATE TABLE Order_Items (
    item_id      INT PRIMARY KEY,
    order_id     INT,
    book_id      INT,
    quantity     INT,
    created_at   DATE,
    status       VARCHAR(50),
    total_price  DECIMAL(10,2),   -- ← DERIVED, violates 3NF
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);
```

**After (3NF compliant):**
```sql
CREATE TABLE Order_Items (
    item_id    INT PRIMARY KEY,
    order_id   INT NOT NULL,
    book_id    INT NOT NULL,
    quantity   INT NOT NULL CHECK (quantity > 0),
    created_at DATE DEFAULT (CURRENT_DATE),
    status     VARCHAR(50) DEFAULT 'ok',
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (book_id)  REFERENCES Books(book_id)
);
```

`total_price` is now computed in SQL as:
```sql
SELECT oi.item_id, oi.quantity, b.price, (oi.quantity * b.price) AS total_price
FROM Order_Items oi
JOIN Books b ON oi.book_id = b.book_id;
```

### Step 3 — Verify remaining tables

No further decomposition is needed. All other attributes in Users, Books, and Orders depend solely and directly on their respective primary keys.

---

## 6. Final Relational Schema (3NF)

```
Users(
    user_id    INT          PK,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    created_at DATE,
    updated_at DATE,
    status     VARCHAR(50)  DEFAULT 'active'
)

Books(
    book_id        INT            PK,
    title          VARCHAR(200)   NOT NULL,
    author         VARCHAR(150),
    price          DECIMAL(10,2)  NOT NULL CHECK (price >= 0),
    published_date DATE,
    created_at     DATE,
    status         VARCHAR(50)    DEFAULT 'available'
)

Orders(
    order_id   INT         PK,
    user_id    INT         NOT NULL  FK → Users(user_id),
    order_date DATE,
    created_at DATE,
    status     VARCHAR(50) DEFAULT 'pending'
)

Order_Items(
    item_id    INT          PK,
    order_id   INT NOT NULL FK → Orders(order_id),
    book_id    INT NOT NULL FK → Books(book_id),
    quantity   INT NOT NULL CHECK (quantity > 0),
    created_at DATE,
    status     VARCHAR(50)  DEFAULT 'ok'
    -- total_price REMOVED: computed as quantity * Books.price
)
```

### Entity-Relationship Summary

```
Users ──< Orders ──< Order_Items >── Books
 (1)      (many)      (many)          (1)
```

- **Users → Orders:** One-to-Many (a user can place many orders)
- **Orders → Order_Items:** One-to-Many (an order can contain many items)
- **Books → Order_Items:** One-to-Many (a book can appear in many order items)

---

## 7. Summary of Changes

| Change | Reason |
|---|---|
| Removed `Order_Items.total_price` | Derived column — transitive dependency violates 3NF |
| Added `CHECK (price >= 0)` on Books | Data integrity — prevents negative prices |
| Added `CHECK (quantity > 0)` on Order_Items | Data integrity — quantity must be positive |
| Added `NOT NULL` constraints | Enforce required fields |
| Added `UNIQUE` on `Users.email` | Already in DML; formalized in DDL |
| Added `author` column to Books | Practical field missing from original schema |

All four tables now satisfy **First, Second, and Third Normal Form**.
