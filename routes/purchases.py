from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection
from datetime import datetime
from routes.analytics import update_season_stats, check_demand_spike

bp = Blueprint('purchases', __name__)

@bp.route('/purchases', methods=('GET', 'POST'))
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
            prev_purchase = conn.execute(
                'SELECT * FROM Purchase WHERE item_id = ? ORDER BY purchase_date DESC, id DESC LIMIT 1',
                (item_id,)
            ).fetchone()

            conn.execute('''INSERT INTO Purchase (item_id, quantity_bought, purchase_price_per_unit, total_cost, stock_left_before_purchase, purchase_date)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                         (item_id, quantity_bought, purchase_price_per_unit, total_cost, stock_left_before_purchase, purchase_date))

            conn.execute('UPDATE Item SET current_stock = ? WHERE id = ?',
                         (stock_left_before_purchase + quantity_bought, item_id))

            consumption = 0
            daily_usage = 0
            if prev_purchase:
                prev_qty = prev_purchase['quantity_bought']
                prev_stock_left = prev_purchase['stock_left_before_purchase']
                stock_after_prev_purchase = prev_stock_left + prev_qty
                consumption = stock_after_prev_purchase - stock_left_before_purchase

                prev_date = datetime.strptime(prev_purchase['purchase_date'], '%Y-%m-%d').date()
                curr_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                days_between = (curr_date - prev_date).days

                daily_usage = consumption / days_between if days_between > 0 else 0

                # Check for spike
                if check_demand_spike(conn, item_id, daily_usage):
                    flash(f'Demand Spike Alert! Usage increased significantly.')

                update_season_stats(conn, item_id, purchase_date, consumption)

            if prev_purchase and daily_usage > 0:
                monthly_demand = daily_usage * 30
                stats = conn.execute('SELECT * FROM Item_Stats WHERE item_id = ?', (item_id,)).fetchone()
                if stats:
                    conn.execute('UPDATE Item_Stats SET daily_usage = ?, monthly_demand = ?, last_updated = CURRENT_TIMESTAMP WHERE item_id = ?',
                                 (daily_usage, monthly_demand, item_id))
                else:
                    conn.execute('INSERT INTO Item_Stats (item_id, daily_usage, monthly_demand, last_updated) VALUES (?, ?, ?, CURRENT_TIMESTAMP)',
                                 (item_id, daily_usage, monthly_demand))

            conn.commit()
            return redirect(url_for('purchases.purchases'))

    purchases = conn.execute('SELECT p.*, i.name as item_name FROM Purchase p LEFT JOIN Item i ON p.item_id = i.id').fetchall()
    items = conn.execute('SELECT * FROM Item').fetchall()
    conn.close()
    return render_template('purchases.html', purchases=purchases, items=items)
