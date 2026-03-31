from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection

bp = Blueprint('categories', __name__)

@bp.route('/categories', methods=('GET', 'POST'))
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
            return redirect(url_for('categories.categories'))

    categories = conn.execute('SELECT * FROM Category').fetchall()
    conn.close()
    return render_template('categories.html', categories=categories)

@bp.route('/categories/edit/<int:id>', methods=('GET', 'POST'))
def edit_category(id):
    conn = get_db_connection()
    category = conn.execute('SELECT * FROM Category WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if not name:
            flash('Name is required!')
        else:
            conn.execute('UPDATE Category SET name = ?, description = ? WHERE id = ?', (name, description, id))
            conn.commit()
            return redirect(url_for('categories.categories'))

    conn.close()
    return render_template('edit_category.html', category=category)

@bp.route('/categories/delete/<int:id>', methods=('POST',))
def delete_category(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Category WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Category deleted successfully!')
    return redirect(url_for('categories.categories'))
