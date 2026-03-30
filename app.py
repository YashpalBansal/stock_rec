import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
import os
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key')

def get_db_connection():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

from datetime import datetime

@app.route('/')
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM Item').fetchall()
    categories = conn.execute('SELECT * FROM Category').fetchall()

    # Calculate Total Inventory Value
    total_inventory_value = 0
    item_details = []
    dead_stock_count = 0

    for item in items:
        # Get latest purchase price
        latest_purchase = conn.execute('SELECT purchase_price_per_unit, purchase_date FROM Purchase WHERE item_id = ? ORDER BY purchase_date DESC LIMIT 1', (item['id'],)).fetchone()
        latest_price = latest_purchase['purchase_price_per_unit'] if latest_purchase else 0
        total_inventory_value += (item['current_stock'] * latest_price)

        # Get Item_Stats for classification
        stats = conn.execute('SELECT * FROM Item_Stats WHERE item_id = ?', (item['id'],)).fetchone()

        # Classification Logic (Simplified based on README)
        classification = "Unknown"
        days_since_purchase = 0
        if latest_purchase:
            last_date = datetime.strptime(latest_purchase['purchase_date'], '%Y-%m-%d').date()
            days_since_purchase = (datetime.now().date() - last_date).days

        if stats and stats['daily_usage'] > 0:
            # Need a baseline for "Top 30%" vs "Bottom" as per README, simplifying to a threshold for this example
            if stats['daily_usage'] > 5:
                classification = "Fast"
            elif stats['daily_usage'] < 1:
                classification = "Slow"
            else:
                classification = "Medium"

        # Dead Stock Rule
        if days_since_purchase > 90 and (not stats or stats['daily_usage'] == 0):
             classification = "Dead"
             dead_stock_count += 1

        item_details.append({
            'name': item['name'],
            'current_stock': item['current_stock'],
            'days_since_purchase': days_since_purchase,
            'classification': classification
        })

    conn.close()
    return render_template('index.html', items=items, categories=categories,
                           total_inventory_value=total_inventory_value,
                           dead_stock_count=dead_stock_count,
                           item_details=item_details)


@app.route('/categories', methods=('GET', 'POST'))
def categories():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if not name:
            flash('Name is required!')
        else:
            conn.execute('INSERT INTO Category (name, description) VALUES (?, ?)', (name, description))
            conn.commit()
            return redirect(url_for('categories'))

    categories = conn.execute('SELECT * FROM Category').fetchall()
    conn.close()
    return render_template('categories.html', categories=categories)

@app.route('/items', methods=('GET', 'POST'))
def items():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        category_id = request.form['category_id']
        unit = request.form['unit']
        current_stock = request.form['current_stock']

        if not name or not category_id:
            flash('Name and Category are required!')
        else:
            conn.execute('INSERT INTO Item (name, category_id, unit, current_stock) VALUES (?, ?, ?, ?)',
                         (name, category_id, unit, current_stock))
            conn.commit()
            return redirect(url_for('items'))

    items = conn.execute('SELECT i.*, c.name as category_name FROM Item i LEFT JOIN Category c ON i.category_id = c.id').fetchall()
    categories = conn.execute('SELECT * FROM Category').fetchall()
    conn.close()
    return render_template('items.html', items=items, categories=categories)

from datetime import datetime

@app.route('/purchases', methods=('GET', 'POST'))
def purchases():
    conn = get_db_connection()
    if request.method == 'POST':
        item_id = request.form['item_id']
        quantity_bought = float(request.form['quantity_bought'])
        purchase_price_per_unit = float(request.form['purchase_price_per_unit'])
        total_cost = float(request.form['total_cost'])
        stock_left_before_purchase = float(request.form['stock_left_before_purchase'])
        purchase_date = request.form['purchase_date']

        if not item_id:
            flash('Item is required!')
        else:
            # Query the previous purchase for the same item
            prev_purchase = conn.execute(
                'SELECT * FROM Purchase WHERE item_id = ? ORDER BY purchase_date DESC, id DESC LIMIT 1',
                (item_id,)
            ).fetchone()

            conn.execute('''INSERT INTO Purchase (item_id, quantity_bought, purchase_price_per_unit, total_cost, stock_left_before_purchase, purchase_date)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                         (item_id, quantity_bought, purchase_price_per_unit, total_cost, stock_left_before_purchase, purchase_date))

            # Update current stock
            conn.execute('UPDATE Item SET current_stock = ? WHERE id = ?',
                         (stock_left_before_purchase + quantity_bought, item_id))

            # Calculate Consumption and Daily Usage
            if prev_purchase:
                prev_qty = prev_purchase['quantity_bought']
                prev_stock_left = prev_purchase['stock_left_before_purchase']
                # Actual stock available after previous purchase
                stock_after_prev_purchase = prev_stock_left + prev_qty
                consumption = stock_after_prev_purchase - stock_left_before_purchase

                # Calculate Days Between Purchases
                prev_date = datetime.strptime(prev_purchase['purchase_date'], '%Y-%m-%d').date()
                curr_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                days_between = (curr_date - prev_date).days

                if days_between > 0:
                    daily_usage = consumption / days_between
                else:
                    daily_usage = 0
            else:
                consumption = 0
                daily_usage = 0

            # Write to Item_Stats table
            if prev_purchase and daily_usage > 0:
                monthly_demand = daily_usage * 30
                # Check if item stats exists
                stats = conn.execute('SELECT * FROM Item_Stats WHERE item_id = ?', (item_id,)).fetchone()
                if stats:
                    conn.execute('UPDATE Item_Stats SET daily_usage = ?, monthly_demand = ?, last_updated = CURRENT_TIMESTAMP WHERE item_id = ?',
                                 (daily_usage, monthly_demand, item_id))
                else:
                    conn.execute('INSERT INTO Item_Stats (item_id, daily_usage, monthly_demand, last_updated) VALUES (?, ?, ?, CURRENT_TIMESTAMP)',
                                 (item_id, daily_usage, monthly_demand))

            conn.commit()
            return redirect(url_for('purchases'))

    purchases = conn.execute('SELECT p.*, i.name as item_name FROM Purchase p LEFT JOIN Item i ON p.item_id = i.id').fetchall()
    items = conn.execute('SELECT * FROM Item').fetchall()
    conn.close()
    return render_template('purchases.html', purchases=purchases, items=items)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
