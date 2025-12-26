from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from db import get_db_connection

order_bp = Blueprint('order', __name__, url_prefix='/order')

@order_bp.route('/<int:order_id>')
def order_confirmation(order_id):
    if 'customer_id' not in session:
        return redirect(url_for('customer.login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get order details
        cursor.execute("""
            SELECT o.*, c.email, c.first_name, c.last_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE o.id = %s AND o.customer_id = %s
        """, (order_id, session['customer_id']))

        order = cursor.fetchone()

        if not order:
            cursor.close()
            conn.close()
            flash('Bestellung nicht gefunden.', 'error')
            return redirect('/')

        # Get order items
        cursor.execute("""
            SELECT oi.*, p.titel
            FROM order_items oi
            JOIN produkte p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order_id,))

        order_items = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('order/confirmation.html', order=order, order_items=order_items)

    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect('/')

@order_bp.route('/history')
def order_history():
    if 'customer_id' not in session:
        return redirect(url_for('customer.login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get all orders for this customer
        cursor.execute("""
            SELECT o.*,
                   (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as item_count
            FROM orders o
            WHERE o.customer_id = %s
            ORDER BY o.order_date DESC
        """, (session['customer_id'],))

        orders = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('order/history.html', orders=orders)

    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect('/')
