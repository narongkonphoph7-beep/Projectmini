-- Douceur Database Schema

CREATE TABLE IF NOT EXISTS Products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL DEFAULT 'เบเกอรี่',
    cost_price DECIMAL(10,2) NOT NULL DEFAULT 0,
    selling_price DECIMAL(10,2) NOT NULL DEFAULT 0,
    low_stock_threshold INT NOT NULL DEFAULT 10
);

CREATE TABLE IF NOT EXISTS Inventory (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES Products(id) ON DELETE CASCADE,
    type VARCHAR(10) NOT NULL CHECK (type IN ('IN', 'OUT')),
    quantity INT NOT NULL DEFAULT 0,
    note TEXT DEFAULT '',
    date DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS Sales (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES Products(id) ON DELETE CASCADE,
    quantity INT NOT NULL DEFAULT 1,
    total_price DECIMAL(10,2) NOT NULL DEFAULT 0,
    payment_type VARCHAR(50) DEFAULT 'เงินสด',
    sale_type VARCHAR(50) DEFAULT 'ทั่วไป',
    date DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS Expenses (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL DEFAULT '',
    amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    date DATE NOT NULL DEFAULT CURRENT_DATE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sales_date ON Sales(date);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON Expenses(date);
CREATE INDEX IF NOT EXISTS idx_sales_product ON Sales(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_product ON Inventory(product_id);
