CREATE TABLE IF NOT EXISTS Category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category_id INTEGER,
    unit TEXT,
    current_stock REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES Category(id)
);

CREATE TABLE IF NOT EXISTS Purchase (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    quantity_bought REAL,
    purchase_price_per_unit REAL,
    total_cost REAL,
    stock_left_before_purchase REAL,
    purchase_date DATE,
    FOREIGN KEY (item_id) REFERENCES Item(id)
);

CREATE TABLE IF NOT EXISTS Item_Stats (
    item_id INTEGER PRIMARY KEY,
    daily_usage REAL,
    monthly_demand REAL,
    last_updated TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Season_Stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    season_name TEXT,
    year INTEGER,
    total_consumption REAL,
    season_index REAL
);
