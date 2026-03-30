📦 Smart Inventory & Demand Forecasting System

A region-aware inventory management system with Punjabi season-based demand forecasting, designed to help businesses answer:

«What should I buy, when should I buy, and how much should I buy?»

---

🚀 Features Overview

Core Features

- CRUD for Categories
- CRUD for Items
- Purchase Tracking (with stock-left method)

Intelligence Features

- 💰 Purchase Price Tracking
- 📈 Price Trend Analysis
- 💵 Inventory Value Calculation
- 🧊 Dead Stock Detection
- ⚡ Fast / Slow Moving Classification
- 📊 Monthly Demand Trends
- 🌾 Punjabi Seasonality Detection
- 🚨 Demand Spike Alerts
- 📉 Business Dashboard

---

🧠 Key Concept: Stock-Left Consumption Model

Instead of tracking daily usage, the system calculates consumption between purchases.

Formula:

Consumption = Previous Purchase Quantity - Stock Left at Reorder

Daily Usage = Consumption / Days Between Purchases

---

🗄️ Database Schema (SQLite3)

1. Category Table

CREATE TABLE Category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

---

2. Item Table

CREATE TABLE Item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category_id INTEGER,
    unit TEXT,
    current_stock REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES Category(id)
);

---

3. Purchase Table

CREATE TABLE Purchase (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    quantity_bought REAL,
    purchase_price_per_unit REAL,
    total_cost REAL,
    stock_left_before_purchase REAL,
    purchase_date DATE,
    FOREIGN KEY (item_id) REFERENCES Item(id)
);

---

4. Derived Table (Optional)

CREATE TABLE Item_Stats (
    item_id INTEGER PRIMARY KEY,
    daily_usage REAL,
    monthly_demand REAL,
    last_updated TIMESTAMP
);

---

5. Season Stats Table

CREATE TABLE Season_Stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    season_name TEXT,
    year INTEGER,
    total_consumption REAL,
    season_index REAL
);

---

🌾 Punjabi Season Mapping

Punjabi Month| Approx Time| Season
Chet| Mar–Apr| Spring
Vaisakh| Apr–May| Summer
Jeth| May–Jun| Peak Summer
Harr| Jun–Jul| Pre-Monsoon
Saun| Jul–Aug| Rainy
Bhado| Aug–Sep| Rainy
Assu| Sep–Oct| Autumn
Katak| Oct–Nov| Festive
Maghar| Nov–Dec| Winter
Poh| Dec–Jan| Peak Winter
Magh| Jan–Feb| Winter
Phagun| Feb–Mar| Spring

---

🔄 Core Processing Flow

New Purchase Added
        ↓
Fetch Previous Purchase
        ↓
Calculate Consumption
        ↓
Calculate Daily Usage
        ↓
Update Monthly Demand
        ↓
Update Seasonality Data
        ↓
Check Demand Spike
        ↓
Update Classification
        ↓
Refresh Dashboard

---

📊 Feature Implementations

💰 1. Purchase Price Tracking

- Store price per unit and total cost
- Enables trend + valuation

---

📈 2. Price Trend Tracking

Example:

Jan → ₹100
Feb → ₹110
Mar → ₹105

---

💵 3. Inventory Value

Basic:

Inventory Value = Current Stock × Latest Price

Advanced:

Weighted Avg Price = Total Cost / Total Quantity

---

🧊 4. Dead Stock Detection

Rule:

If no significant consumption for X days → Dead Stock

Thresholds:

- 30 days → Slow
- 60 days → Warning
- 90 days → Dead

---

⚡ 5. Fast / Slow Moving Classification

Based on daily usage:

- Top 30% → Fast
- Middle → Medium
- Bottom → Slow

---

📊 6. Monthly Demand Trends

Month → Total Consumption

---

🌾 7. Seasonality Detection

Season Index = Season Avg / Overall Avg

---

🚨 8. Demand Spike Alerts

If current usage > 1.5 × average → Spike

---

📊 9. Dashboard

Top Metrics:

- Total Inventory Value
- Total Items
- Dead Stock Count
- Alerts

Table:

| Item | Stock | Days Left | Trend | Type |

Charts:

- Monthly Demand
- Price Trends
- Seasonality

---

⚙️ Tech Stack

Backend

- Python
- Flask (REST APIs)

Database

- SQLite3 (lightweight, local storage)

Frontend

- HTML
- CSS
- JavaScript (Vanilla or with small libraries)

---

🧪 Example Workflow

1. Add Item
2. Record Purchase
3. Next Purchase → enter stock left
4. System calculates:
   - Consumption
   - Daily usage
   - Trends
5. Dashboard updates

---

🚀 Future Enhancements

- ML-based forecasting
- Notifications (SMS/WhatsApp)
- Supplier optimization
- Multi-user roles
- Cloud sync

---

💡 Key Insight

«This system transforms inventory data into business decisions.»

---

📌 Conclusion

You are building:

✅ Inventory Manager
✅ Forecast Engine
✅ Localized Business Intelligence Tool

---

📄 License

MIT License
