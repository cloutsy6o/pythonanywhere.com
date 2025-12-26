from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
from db import get_db_connection

address_bp = Blueprint('address', __name__, url_prefix='/address')

@address_bp.route('/manage')
def manage_addresses():
    if 'customer_id' not in session:
        return redirect(url_for('customer.login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM customer_addresses
            WHERE customer_id = %s
            ORDER BY is_default DESC, updated_at DESC
        """, (session['customer_id'],))

        addresses = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('address/manage.html', addresses=addresses)

    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect('/cart/checkout')

@address_bp.route('/add', methods=['POST'])
def add_address():
    if 'customer_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    try:
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        # If setting as default, unset other defaults
        if data.get('is_default'):
            cursor.execute("""
                UPDATE customer_addresses
                SET is_default = FALSE
                WHERE customer_id = %s
            """, (session['customer_id'],))

        cursor.execute("""
            INSERT INTO customer_addresses
            (customer_id, full_name, address_line1, address_line2,
             city, state, zip_code, country, phone, is_default)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session['customer_id'],
            data.get('full_name', '').strip(),
            data.get('address_line1', '').strip(),
            data.get('address_line2', '').strip(),
            data.get('city', '').strip(),
            data.get('state', '').strip(),
            data.get('zip_code', '').strip(),
            data.get('country', 'Deutschland').strip(),
            data.get('phone', '').strip(),
            data.get('is_default', False)
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@address_bp.route('/delete/<int:address_id>', methods=['POST'])
def delete_address(address_id):
    if 'customer_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM customer_addresses
            WHERE id = %s AND customer_id = %s
        """, (address_id, session['customer_id']))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@address_bp.route('/set-default/<int:address_id>', methods=['POST'])
def set_default_address(address_id):
    if 'customer_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Unset all defaults
        cursor.execute("""
            UPDATE customer_addresses
            SET is_default = FALSE
            WHERE customer_id = %s
        """, (session['customer_id'],))

        # Set new default
        cursor.execute("""
            UPDATE customer_addresses
            SET is_default = TRUE
            WHERE id = %s AND customer_id = %s
        """, (address_id, session['customer_id']))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@address_bp.route('/get-default')
def get_default_address():
    if 'customer_id' not in session:
        return jsonify({'address': None})

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM customer_addresses
            WHERE customer_id = %s AND is_default = TRUE
            LIMIT 1
        """, (session['customer_id'],))

        address = cursor.fetchone()
        cursor.close()
        conn.close()

        return jsonify({'address': address})

    except Exception as e:
        return jsonify({'address': None})
