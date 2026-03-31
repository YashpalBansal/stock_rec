from flask import Blueprint, render_template
from db import get_db_connection
from datetime import datetime
from routes.analytics import calculate_weighted_avg_price

bp = Blueprint('dashboard', __name__)

@bp.route('/')
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM Item').fetchall()
    categories = conn.execute('SELECT * FROM Category').fetchall()

    total_inventory_value = 0
    item_details = []
    dead_stock_count = 0
    alerts_count = 0

    for item in items:
        latest_purchase = conn.execute('SELECT purchase_price_per_unit, purchase_date FROM Purchase WHERE item_id = ? ORDER BY purchase_date DESC LIMIT 1', (item['id'],)).fetchone()

        # Advanced Inventory Value: Weighted Avg Price
        weighted_avg = calculate_weighted_avg_price(conn, item['id'])
        price_to_use = weighted_avg if weighted_avg > 0 else (latest_purchase['purchase_price_per_unit'] if latest_purchase else 0)
        total_inventory_value += (item['current_stock'] * price_to_use)

        stats = conn.execute('SELECT * FROM Item_Stats WHERE item_id = ?', (item['id'],)).fetchone()

        classification = "Unknown"
        days_since_purchase = 0
        if latest_purchase:
            last_date = datetime.strptime(latest_purchase['purchase_date'], '%Y-%m-%d').date()
            days_since_purchase = (datetime.now().date() - last_date).days

        if stats and stats['daily_usage'] > 0:
            if stats['daily_usage'] > 5:
                classification = "Fast"
            elif stats['daily_usage'] < 1:
                classification = "Slow"
            else:
                classification = "Medium"

        if days_since_purchase > 90 and (not stats or stats['daily_usage'] == 0):
             classification = "Dead"
             dead_stock_count += 1

        # Alerts count logic (e.g. items with days > 60 Warning, or Dead)
        if days_since_purchase > 60:
            alerts_count += 1

        # Price Trends (last 3 purchases)
        price_history = conn.execute('SELECT purchase_price_per_unit, purchase_date FROM Purchase WHERE item_id = ? ORDER BY purchase_date DESC LIMIT 3', (item['id'],)).fetchall()
        price_trend = " -> ".join([f"₹{p['purchase_price_per_unit']}" for p in price_history[::-1]])

        item_details.append({
            'name': item['name'],
            'current_stock': item['current_stock'],
            'days_since_purchase': days_since_purchase,
            'classification': classification,
            'price_trend': price_trend
        })

    conn.close()
    return render_template('index.html', items=items, categories=categories,
                           total_inventory_value=total_inventory_value,
                           dead_stock_count=dead_stock_count,
                           alerts_count=alerts_count,
                           item_details=item_details)
