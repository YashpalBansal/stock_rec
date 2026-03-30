import sqlite3, os
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key')

def get_db():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db()
    items = conn.execute('SELECT * FROM Item').fetchall()
    total_val, dead_stock, details = 0, 0, []

    for item in items:
        p = conn.execute('SELECT purchase_price_per_unit as price, purchase_date as date FROM Purchase WHERE item_id = ? ORDER BY date DESC LIMIT 1', (item['id'],)).fetchone()
        price = p['price'] if p else 0
        total_val += (item['current_stock'] * price)
        stats = conn.execute('SELECT * FROM Item_Stats WHERE item_id = ?', (item['id'],)).fetchone()

        cls, days = "Unknown", 0
        if p:
            days = (datetime.now().date() - datetime.strptime(p['date'], '%Y-%m-%d').date()).days

        if stats and stats['daily_usage'] > 0:
            cls = "Fast" if stats['daily_usage'] > 5 else ("Slow" if stats['daily_usage'] < 1 else "Medium")

        if days > 90 and (not stats or stats['daily_usage'] == 0):
             cls, dead_stock = "Dead", dead_stock + 1

        details.append({'name': item['name'], 'current_stock': item['current_stock'], 'days_since_purchase': days, 'classification': cls})

    conn.close()
    return render_template('index.html', items=items, total_inventory_value=total_val, dead_stock_count=dead_stock, item_details=details)

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    conn = get_db()
    if request.method == 'POST':
        name, desc = request.form['name'], request.form['description']
        if name:
            conn.execute('INSERT INTO Category (name, description) VALUES (?, ?)', (name, desc))
            conn.commit()
            return redirect(url_for('categories'))
        flash('Name required!')
    cats = conn.execute('SELECT * FROM Category').fetchall()
    conn.close()
    return render_template('categories.html', categories=cats)

@app.route('/items', methods=['GET', 'POST'])
def items():
    conn = get_db()
    if request.method == 'POST':
        n, c, u, s = request.form['name'], request.form['category_id'], request.form['unit'], request.form['current_stock']
        if n and c:
            conn.execute('INSERT INTO Item (name, category_id, unit, current_stock) VALUES (?, ?, ?, ?)', (n, c, u, s))
            conn.commit()
            return redirect(url_for('items'))
        flash('Name and Category required!')
    items = conn.execute('SELECT i.*, c.name as category_name FROM Item i LEFT JOIN Category c ON i.category_id = c.id').fetchall()
    cats = conn.execute('SELECT * FROM Category').fetchall()
    conn.close()
    return render_template('items.html', items=items, categories=cats)

@app.route('/purchases', methods=['GET', 'POST'])
def purchases():
    conn = get_db()
    if request.method == 'POST':
        f = request.form
        i_id, q, p, c, s, d = f['item_id'], float(f['quantity_bought']), float(f['purchase_price_per_unit']), float(f['total_cost']), float(f['stock_left_before_purchase']), f['purchase_date']
        if i_id:
            prev = conn.execute('SELECT * FROM Purchase WHERE item_id = ? ORDER BY purchase_date DESC LIMIT 1', (i_id,)).fetchone()
            conn.execute('INSERT INTO Purchase (item_id, quantity_bought, purchase_price_per_unit, total_cost, stock_left_before_purchase, purchase_date) VALUES (?, ?, ?, ?, ?, ?)', (i_id, q, p, c, s, d))
            conn.execute('UPDATE Item SET current_stock = ? WHERE id = ?', (s + q, i_id))

            if prev:
                days = (datetime.strptime(d, '%Y-%m-%d').date() - datetime.strptime(prev['purchase_date'], '%Y-%m-%d').date()).days
                daily = (prev['stock_left_before_purchase'] + prev['quantity_bought'] - s) / days if days > 0 else 0
                if daily > 0:
                    st = conn.execute('SELECT * FROM Item_Stats WHERE item_id = ?', (i_id,)).fetchone()
                    if st: conn.execute('UPDATE Item_Stats SET daily_usage=?, monthly_demand=?, last_updated=CURRENT_TIMESTAMP WHERE item_id=?', (daily, daily*30, i_id))
                    else: conn.execute('INSERT INTO Item_Stats (item_id, daily_usage, monthly_demand, last_updated) VALUES (?, ?, ?, CURRENT_TIMESTAMP)', (i_id, daily, daily*30))
            conn.commit()
            return redirect(url_for('purchases'))
        flash('Item required!')

    ps = conn.execute('SELECT p.*, i.name as item_name FROM Purchase p LEFT JOIN Item i ON p.item_id = i.id').fetchall()
    its = conn.execute('SELECT * FROM Item').fetchall()
    conn.close()
    return render_template('purchases.html', purchases=ps, items=its)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
