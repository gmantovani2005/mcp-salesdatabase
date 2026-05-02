CREATE TABLE category (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE region (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE payment_method (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE product (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES category(id),
    unit_price  DECIMAL(10, 2) NOT NULL
);

CREATE TABLE sales_order (
    id                INTEGER PRIMARY KEY,
    date              DATE NOT NULL,
    product_id        INTEGER NOT NULL REFERENCES product(id),
    region_id         INTEGER NOT NULL REFERENCES region(id),
    payment_method_id INTEGER NOT NULL REFERENCES payment_method(id),
    units_sold        INTEGER NOT NULL,
    unit_price        DECIMAL(10, 2) NOT NULL,
    total_revenue     DECIMAL(10, 2) NOT NULL
);
