from flask import Blueprint, render_template, session, redirect, flash, request, make_response
from db import get_db_connection
import csv
import io
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/panel')
def admin_panel():
    if not session.get('logged_in'):
        return redirect('/login?next=admin/panel')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM countries")
        countries = cursor.fetchall()

        cursor.execute("SELECT * FROM regions")
        regions = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('admin-panel.html',
                             countries=countries,
                             regions=regions)

    except Exception as e:
        return f"❌ Datenbankfehler: {str(e)}"

@admin_bp.route('/dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect('/login?next=admin/dashboard')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        today = datetime.now().date()
        last_30_days = today - timedelta(days=30)

        # 1. Total orders count
        cursor.execute("SELECT COUNT(*) as total FROM orders")
        total_orders = cursor.fetchone()['total']

        # 2. Today's orders
        cursor.execute("SELECT COUNT(*) as today FROM orders WHERE DATE(order_date) = %s", (today,))
        today_orders = cursor.fetchone()['today']

        # 3. Last 30 days orders
        cursor.execute("SELECT COUNT(*) as last_month FROM orders WHERE order_date >= %s", (last_30_days,))
        last_month_orders = cursor.fetchone()['last_month']

        # 4. Revenue stats
        cursor.execute("SELECT SUM(total_amount) as total_revenue FROM orders WHERE status != 'cancelled'")
        total_revenue = cursor.fetchone()['total_revenue'] or 0

        cursor.execute("SELECT SUM(total_amount) as today_revenue FROM orders WHERE DATE(order_date) = %s AND status != 'cancelled'", (today,))
        today_revenue = cursor.fetchone()['today_revenue'] or 0

        cursor.execute("SELECT SUM(total_amount) as month_revenue FROM orders WHERE order_date >= %s AND status != 'cancelled'", (last_30_days,))
        month_revenue = cursor.fetchone()['month_revenue'] or 0

        # 5. Status distribution
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM orders
            GROUP BY status
            ORDER BY count DESC
        """)
        status_stats = cursor.fetchall()

        # 6. Recent orders (last 10)
        cursor.execute("""
            SELECT o.*, c.first_name, c.last_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            ORDER BY order_date DESC
            LIMIT 10
        """)
        recent_orders = cursor.fetchall()

        # 7. Top customers by order count
        cursor.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email,
                   COUNT(o.id) as order_count,
                   SUM(o.total_amount) as total_spent
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            GROUP BY c.id
            ORDER BY order_count DESC
            LIMIT 5
        """)
        top_customers = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('admin/dashboard.html',
                             total_orders=total_orders,
                             today_orders=today_orders,
                             last_month_orders=last_month_orders,
                             total_revenue=total_revenue,
                             today_revenue=today_revenue,
                             month_revenue=month_revenue,
                             status_stats=status_stats,
                             recent_orders=recent_orders,
                             top_customers=top_customers,
                             today_date=today.strftime('%d.%m.%Y'))

    except Exception as e:
        return f"❌ Dashboard-Fehler: {str(e)}"

@admin_bp.route('/orders')
def admin_orders():
    if not session.get('logged_in'):
        return redirect('/login?next=admin/orders')

    try:
        # Get search parameters
        search_query = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')

        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Build query with filters
        query = """
            SELECT o.*, c.email, c.first_name, c.last_name, c.phone,
                   (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as item_count
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE 1=1
        """
        count_query = "SELECT COUNT(*) as total FROM orders o JOIN customers c ON o.customer_id = c.id WHERE 1=1"
        params = []

        # Search filter
        if search_query:
            if search_query.isdigit():
                query += " AND o.id = %s"
                count_query += " AND o.id = %s"
                params.append(int(search_query))
            else:
                query += " AND (c.email LIKE %s OR c.first_name LIKE %s OR c.last_name LIKE %s)"
                count_query += " AND (c.email LIKE %s OR c.first_name LIKE %s OR c.last_name LIKE %s)"
                params.append(f"%{search_query}%")
                params.append(f"%{search_query}%")
                params.append(f"%{search_query}%")

        # Status filter
        if status_filter:
            query += " AND o.status = %s"
            count_query += " AND o.status = %s"
            params.append(status_filter)

        # Date filters
        if date_from:
            query += " AND DATE(o.order_date) >= %s"
            count_query += " AND DATE(o.order_date) >= %s"
            params.append(date_from)
        if date_to:
            query += " AND DATE(o.order_date) <= %s"
            count_query += " AND DATE(o.order_date) <= %s"
            params.append(date_to)

        # Get total count
        cursor.execute(count_query, params)
        total_result = cursor.fetchone()
        total_orders = total_result['total']

        # Add pagination to main query
        query += " ORDER BY o.order_date DESC LIMIT %s OFFSET %s"
        params.append(per_page)
        params.append((page - 1) * per_page)

        cursor.execute(query, params)
        orders = cursor.fetchall()

        cursor.close()
        conn.close()

        # Calculate pagination values
        total_pages = (total_orders + per_page - 1) // per_page if total_orders > 0 else 1

        return render_template('admin/orders.html',
                             orders=orders,
                             search_query=search_query,
                             status_filter=status_filter,
                             date_from=date_from,
                             date_to=date_to,
                             page=page,
                             per_page=per_page,
                             total_orders=total_orders,
                             total_pages=total_pages)

    except Exception as e:
        return f"❌ Fehler: {str(e)}"

@admin_bp.route('/orders/export')
def export_orders_csv():
    if not session.get('logged_in'):
        return redirect('/login?next=admin/orders')

    try:
        # Get search parameters for filtering export
        search_query = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Build query (same as orders page)
        query = """
            SELECT o.*, c.email, c.first_name, c.last_name, c.phone,
                   (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as item_count
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE 1=1
        """
        params = []

        if search_query:
            if search_query.isdigit():
                query += " AND o.id = %s"
                params.append(int(search_query))
            else:
                query += " AND (c.email LIKE %s OR c.first_name LIKE %s OR c.last_name LIKE %s)"
                params.append(f"%{search_query}%")
                params.append(f"%{search_query}%")
                params.append(f"%{search_query}%")

        if status_filter:
            query += " AND o.status = %s"
            params.append(status_filter)

        if date_from:
            query += " AND DATE(o.order_date) >= %s"
            params.append(date_from)
        if date_to:
            query += " AND DATE(o.order_date) <= %s"
            params.append(date_to)

        query += " ORDER BY o.order_date DESC"

        cursor.execute(query, params)
        orders = cursor.fetchall()

        cursor.close()
        conn.close()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Write header
        writer.writerow([
            'Bestell-Nr', 'Kunde', 'E-Mail', 'Telefon', 'Datum',
            'Artikelanzahl', 'Gesamtbetrag (€)', 'Status', 'Versandadresse',
            'Zahlungsmethode', 'Bestelldatum'
        ])

        # Write data rows
        for order in orders:
            writer.writerow([
                order['id'],
                f"{order['first_name']} {order['last_name']}",
                order['email'],
                order['phone'] or '',
                order['order_date'].strftime('%d.%m.%Y %H:%M'),
                order['item_count'],
                f"{order['total_amount']:.2f}",
                order['status'],
                order['shipping_address'].replace('\n', ' | '),
                order.get('payment_method', ''),
                order['order_date'].strftime('%Y-%m-%d')
            ])

        # Create response with CSV file
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=bestellungen_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        response.headers['Content-type'] = 'text/csv; charset=utf-8'

        return response

    except Exception as e:
        flash(f'Export-Fehler: {str(e)}', 'error')
        return redirect('/admin/orders')

@admin_bp.route('/orders/bulk-update', methods=['POST'])
def bulk_update_orders():
    if not session.get('logged_in'):
        return redirect('/login?next=admin/orders')

    try:
        # Get form data
        order_ids = request.form.getlist('order_ids[]')
        new_status = request.form.get('status')

        if not order_ids:
            flash('Keine Bestellungen ausgewählt.', 'warning')
            return redirect('/admin/orders')

        if not new_status or new_status not in ['pending', 'processing', 'shipped', 'completed', 'cancelled']:
            flash('Ungültiger Status.', 'error')
            return redirect('/admin/orders')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Convert order_ids to integers and create placeholders
        int_order_ids = [int(oid) for oid in order_ids if oid.isdigit()]
        if not int_order_ids:
            cursor.close()
            conn.close()
            flash('Ungültige Bestellnummern.', 'error')
            return redirect('/admin/orders')

        # Update selected orders
        placeholders = ', '.join(['%s'] * len(int_order_ids))
        query = f"UPDATE orders SET status = %s WHERE id IN ({placeholders})"
        params = [new_status] + int_order_ids

        cursor.execute(query, params)
        conn.commit()

        cursor.close()
        conn.close()

        status_text = {
            'pending': 'ausstehend',
            'processing': 'in Bearbeitung',
            'shipped': 'versandt',
            'completed': 'abgeschlossen',
            'cancelled': 'storniert'
        }.get(new_status, new_status)

        flash(f'✅ {len(int_order_ids)} Bestellung(en) erfolgreich auf "{status_text}" aktualisiert.', 'success')
        return redirect('/admin/orders')

    except Exception as e:
        flash(f'Fehler bei der Massenaktualisierung: {str(e)}', 'error')
        return redirect('/admin/orders')

@admin_bp.route('/order/<int:order_id>')
def admin_order_detail(order_id):
    if not session.get('logged_in'):
        return redirect(f'/login?next=admin/order/{order_id}')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT o.*, c.email, c.first_name, c.last_name, c.phone
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE o.id = %s
        """, (order_id,))

        order = cursor.fetchone()

        if not order:
            cursor.close()
            conn.close()
            flash('Bestellung nicht gefunden.', 'error')
            return redirect('/admin/orders')

        cursor.execute("""
            SELECT oi.*, p.titel, p.beschreibung
            FROM order_items oi
            JOIN produkte p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order_id,))

        order_items = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('admin/order_detail.html', order=order, order_items=order_items)

    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect('/admin/orders')

@admin_bp.route('/order/<int:order_id>/update', methods=['GET', 'POST'])
def admin_update_order(order_id):
    if not session.get('logged_in'):
        return redirect(f'/login?next=admin/order/{order_id}/update')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()

        if not order:
            cursor.close()
            conn.close()
            flash('Bestellung nicht gefunden.', 'error')
            return redirect('/admin/orders')

        if request.method == 'POST':
            new_status = request.form.get('status')

            if new_status in ['pending', 'processing', 'shipped', 'completed', 'cancelled']:
                cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (new_status, order_id))
                conn.commit()
                flash(f'✅ Status für Bestellung #{order_id} auf "{new_status}" aktualisiert.', 'success')

            cursor.close()
            conn.close()
            return redirect(f'/admin/order/{order_id}')

        cursor.close()
        conn.close()
        return render_template('admin/update_order.html', order=order)

    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect(f'/admin/order/{order_id}')
