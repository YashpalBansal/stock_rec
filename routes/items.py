from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection

bp = Blueprint('items', __name__)

@bp.route('/items', methods=('GET', 'POST'))
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
            return redirect(url_for('items.items'))

    items = conn.execute('SELECT i.*, c.name as category_name FROM Item i LEFT JOIN Category c ON i.category_id = c.id').fetchall()
    categories = conn.execute('SELECT * FROM Category').fetchall()
    conn.close()
    return render_template('items.html', items=items, categories=categories)

@bp.route('/items/edit/<int:id>', methods=('GET', 'POST'))
def edit_item(id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM Item WHERE id = ?', (id,)).fetchone()
    categories = conn.execute('SELECT * FROM Category').fetchall()

    if request.method == 'POST':
        name = request.form['name']
        category_id = request.form['category_id']
        unit = request.form['unit']
        current_stock = request.form['current_stock']

        if not name or not category_id:
            flash('Name and Category are required!')
        else:
            conn.execute('UPDATE Item SET name = ?, category_id = ?, unit = ?, current_stock = ? WHERE id = ?',
                         (name, category_id, unit, current_stock, id))
            conn.commit()
            return redirect(url_for('items.items'))

    conn.close()
    return render_template('edit_item.html', item=item, categories=categories)

@bp.route('/items/delete/<int:id>', methods=('POST',))
def delete_item(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Item WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Item deleted successfully!')
    return redirect(url_for('items.items'))
