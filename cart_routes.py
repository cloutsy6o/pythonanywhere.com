from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
from db import get_db_connection
import traceback

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

def update_cart_count():
    if 'customer_id' not in session:
        session['cart_count'] = 0
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(quantity), 0)
            FROM cart
            WHERE customer_id = %s AND is_saved_for_later = FALSE
        """, (session['customer_id'],))
        session['cart_count'] = cursor.fetchone()[0]
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error updating cart count: {e}")
        session['cart_count'] = 0

def get_cart_product_price(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MIN(aktueller_preis)
            FROM produkt_preise
            WHERE produkt_id = %s
        """, (product_id,))
        price = cursor.fetchone()[0] or 0
        cursor.close()
        conn.close()
        return price
    except Exception as e:
        print(f"Error getting product price: {e}")
        return 0

@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    if 'customer_id' not in session:
        return jsonify({'success': False, 'redirect': '/customer/login'}), 401

    try:
        product_id = request.form.get('product_id', type=int)
        quantity = request.form.get('quantity', 1, type=int)

        if not product_id or quantity < 1:
            return jsonify({'success': False, 'error': 'Invalid input'}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if product exists
        cursor.execute("SELECT id FROM produkte WHERE id = %s", (product_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Product not found'}), 404

        current_price = get_cart_product_price(product_id)

        cursor.execute("""
            SELECT id, quantity FROM cart
            WHERE customer_id = %s AND product_id = %s AND is_saved_for_later = FALSE
        """, (session['customer_id'], product_id))

        item = cursor.fetchone()

        if item:
            new_qty = item['quantity'] + quantity
            cursor.execute("""
                UPDATE cart
                SET quantity = %s, price_at_add = %s, added_at = NOW()
                WHERE id = %s
            """, (new_qty, current_price, item['id']))
        else:
            cursor.execute("""
                INSERT INTO cart (customer_id, product_id, quantity, price_at_add)
                VALUES (%s, %s, %s, %s)
            """, (session['customer_id'], product_id, quantity, current_price))

        conn.commit()
        cursor.close()
        conn.close()

        update_cart_count()
        return jsonify({'success': True, 'count': session['cart_count']})

    except Exception as e:
        print(f"Error adding to cart: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ... rest of the routes remain the same ...

@cart_bp.route('/place-order', methods=['POST'])
def place_order():
    if 'customer_id' not in session:
        flash('Bitte melden Sie sich zuerst an.', 'error')
        return redirect(url_for('customer.login'))

    try:
        # Get form data
        full_name = request.form.get('full_name', '').strip()
        address = request.form.get('address', '').strip()
        zip_code = request.form.get('zip_code', '').strip()
        city = request.form.get('city', '').strip()
        country = request.form.get('country', 'Deutschland').strip()
        phone = request.form.get('phone', '').strip()
        payment_method = request.form.get('payment', 'paypal')

        # Build shipping address
        shipping_address_lines = [full_name, address]
        if phone:
            shipping_address_lines.append(f'Telefon: {phone}')
        shipping_address_lines.append(f'{zip_code} {city}')
        shipping_address_lines.append(country)
        shipping_address = '\n'.join(shipping_address_lines)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get cart items
        cursor.execute("""
            SELECT c.*, p.titel
            FROM cart c
            JOIN produkte p ON c.product_id = p.id
            WHERE c.customer_id = %s AND c.is_saved_for_later = FALSE
        """, (session['customer_id'],))

        cart_items = cursor.fetchall()

        if not cart_items:
            cursor.close()
            conn.close()
            flash('Ihr Warenkorb ist leer.', 'warning')
            return redirect('/cart')

        # Calculate total
        total = 0
        for item in cart_items:
            price = get_cart_product_price(item['product_id'])
            total += price * item['quantity']

        # Create order
        cursor.execute("""
            INSERT INTO orders (customer_id, total_amount, shipping_address, status, payment_method)
            VALUES (%s, %s, %s, 'pending', %s)
        """, (session['customer_id'], total, shipping_address, payment_method))

        order_id = cursor.lastrowid

        # Add order items
        for item in cart_items:
            price = get_cart_product_price(item['product_id'])
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, item['product_id'], item['quantity'], price))

        # Clear cart
        cursor.execute("DELETE FROM cart WHERE customer_id = %s AND is_saved_for_later = FALSE", (session['customer_id'],))

        conn.commit()
        cursor.close()
        conn.close()

        # Update cart count
        session['cart_count'] = 0

        flash(f'✅ Bestellung #{order_id} erfolgreich aufgegeben! Vielen Dank für Ihren Einkauf.', 'success')
        return redirect(url_for('order.order_confirmation', order_id=order_id))

    except Exception as e:
        flash(f'Fehler bei der Bestellung: {str(e)}', 'error')
        return redirect('/cart/checkout')
