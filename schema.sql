-- =============================================================
-- Bookstore Application — Final 3NF Schema
-- CS665 Project 3
-- =============================================================

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS Order_Items;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Books;
DROP TABLE IF EXISTS Users;

-- -------------------------------------------------------------
-- Users Table
-- Stores customer accounts.
-- -------------------------------------------------------------
CREATE TABLE Users (
    user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    created_at DATE         NOT NULL DEFAULT (DATE('now')),
    updated_at DATE         NOT NULL DEFAULT (DATE('now')),
    status     VARCHAR(50)  NOT NULL DEFAULT 'active'
);

-- -------------------------------------------------------------
-- Books Table
-- Stores the book catalog.
-- -------------------------------------------------------------
CREATE TABLE Books (
    book_id        INTEGER        PRIMARY KEY AUTOINCREMENT,
    title          VARCHAR(200)   NOT NULL,
    author         VARCHAR(150)   NOT NULL DEFAULT 'Unknown',
    price          DECIMAL(10,2)  NOT NULL CHECK (price >= 0),
    published_date DATE,
    created_at     DATE           NOT NULL DEFAULT (DATE('now')),
    status         VARCHAR(50)    NOT NULL DEFAULT 'available'
);

-- -------------------------------------------------------------
-- Orders Table
-- Links a user to a set of order items.
-- One-to-Many: Users → Orders
-- -------------------------------------------------------------
CREATE TABLE Orders (
    order_id   INTEGER     PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER     NOT NULL,
    order_date DATE        NOT NULL DEFAULT (DATE('now')),
    created_at DATE        NOT NULL DEFAULT (DATE('now')),
    status     VARCHAR(50) NOT NULL DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- -------------------------------------------------------------
-- Order_Items Table
-- Junction table linking Orders to Books (Many-to-Many resolved).
-- NOTE: total_price has been REMOVED per 3NF normalization.
--       Compute it as: quantity * Books.price in queries.
-- -------------------------------------------------------------
CREATE TABLE Order_Items (
    item_id    INTEGER     PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER     NOT NULL,
    book_id    INTEGER     NOT NULL,
    quantity   INTEGER     NOT NULL CHECK (quantity > 0),
    created_at DATE        NOT NULL DEFAULT (DATE('now')),
    status     VARCHAR(50) NOT NULL DEFAULT 'ok',
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (book_id)  REFERENCES Books(book_id)
);

-- =============================================================
-- Seed Data
-- =============================================================

INSERT INTO Users (name, email, created_at, updated_at, status) VALUES
    ('Alice',   'alice@mail.com',   '2024-01-01', '2024-01-02', 'active'),
    ('Bob',     'bob@mail.com',     '2024-02-01', '2024-02-02', 'active'),
    ('Charlie', 'charlie@mail.com', '2024-03-01', '2024-03-02', 'inactive'),
    ('David',   'david@mail.com',   '2024-04-01', '2024-04-02', 'active'),
    ('Eva',     'eva@mail.com',     '2024-05-01', '2024-05-02', 'active');

INSERT INTO Books (title, author, price, published_date, created_at, status) VALUES
    ('SQL Basics',    'Jane Smith',    20.00, '2020-01-01', '2020-01-05', 'available'),
    ('Python Guide',  'John Doe',      25.00, '2021-02-01', '2021-02-05', 'available'),
    ('ML Intro',      'Sara Lee',      30.00, '2022-03-01', '2022-03-05', 'available'),
    ('AI Advanced',   'Tom Brown',     40.00, '2023-04-01', '2023-04-05', 'available'),
    ('Data Science',  'Emily Clark',   35.00, '2023-05-01', '2023-05-05', 'available');

INSERT INTO Orders (user_id, order_date, created_at, status) VALUES
    (1, '2024-06-01', '2024-06-01', 'completed'),
    (2, '2024-06-02', '2024-06-02', 'completed'),
    (3, '2024-06-03', '2024-06-03', 'pending'),
    (1, '2024-06-04', '2024-06-04', 'completed'),
    (2, '2024-06-05', '2024-06-05', 'pending');

INSERT INTO Order_Items (order_id, book_id, quantity, created_at, status) VALUES
    (1, 1, 2, '2024-06-01', 'ok'),
    (2, 2, 1, '2024-06-02', 'ok'),
    (3, 3, 3, '2024-06-03', 'ok'),
    (4, 4, 1, '2024-06-04', 'ok'),
    (5, 5, 2, '2024-06-05', 'ok');
