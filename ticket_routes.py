from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from db import get_db_connection
from datetime import datetime
import uuid
import os
import json
from werkzeug.utils import secure_filename

ticket_bp = Blueprint('ticket', __name__, url_prefix='/ticket')

# File upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'doc', 'docx', 'xls', 'xlsx', 'zip'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
UPLOAD_FOLDER = 'uploads/tickets'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_files(files, ticket_id, message_id):
    """Save uploaded files and return attachment data"""
    attachments = []

    if not files:
        return attachments

    # Ensure upload directory exists
    upload_dir = os.path.join(UPLOAD_FOLDER, str(ticket_id), str(message_id))
    os.makedirs(upload_dir, exist_ok=True)

    for file in files:
        if file and file.filename and file.filename != '':
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(upload_dir, filename)

                # Check file size
                file.seek(0, os.SEEK_END)
                file_length = file.tell()
                file.seek(0, 0)

                if file_length > MAX_FILE_SIZE:
                    continue  # Skip oversized files

                # Save file
                file.save(filepath)

                # Store attachment info with web-accessible path
                web_path = f"tickets/{ticket_id}/{message_id}/{filename}"
                attachments.append({
                    'filename': filename,
                    'path': web_path,  # Web-accessible path (relative to uploads/)
                    'size': file_length,
                    'type': filename.rsplit('.', 1)[1].lower()
                })

    return attachments

# Helper function to generate ticket number
def generate_ticket_number():
    return f"TKT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

# Customer creates new ticket
@ticket_bp.route('/create', methods=['GET', 'POST'])
def create_ticket():
    if request.method == 'GET':
        return render_template('ticket/create.html')

    try:
        # Get form data
        customer_name = request.form.get('name', '').strip()
        customer_email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        category = request.form.get('category', 'other')
        order_id = request.form.get('order_id', '').strip()

        # Validate required fields
        if not all([customer_name, customer_email, subject, description]):
            flash('Bitte füllen Sie alle Pflichtfelder aus.', 'error')
            return redirect(url_for('ticket.create_ticket'))

        # Get customer_id if logged in
        customer_id = session.get('customer_id') if 'customer_id' in session else None

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Create ticket
        ticket_number = generate_ticket_number()

        cursor.execute("""
            INSERT INTO tickets
            (ticket_number, customer_id, customer_name, customer_email,
             subject, description, priority, category, order_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (ticket_number, customer_id, customer_name, customer_email,
              subject, description, priority, category, order_id if order_id else None))

        ticket_id = cursor.lastrowid

        # Handle file uploads if any
        attachments_data = []
        if 'attachments[]' in request.files:
            files = request.files.getlist('attachments[]')
            attachments_data = save_uploaded_files(files, ticket_id, 0)  # message_id 0 for initial

        # Add first message with attachments
        cursor.execute("""
            INSERT INTO ticket_messages (ticket_id, sender_type, message, attachments)
            VALUES (%s, 'customer', %s, %s)
        """, (ticket_id, description, json.dumps(attachments_data) if attachments_data else None))

        conn.commit()
        cursor.close()
        conn.close()

        # TODO: Send confirmation email

        flash(f'✅ Ticket #{ticket_number} wurde erstellt. Wir antworten innerhalb von 24 Stunden.', 'success')
        return redirect(url_for('ticket.view_ticket', ticket_number=ticket_number))

    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect(url_for('ticket.create_ticket'))

# Customer views their ticket
@ticket_bp.route('/view/<ticket_number>')
def view_ticket(ticket_number):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get ticket
        cursor.execute("""
            SELECT t.*, c.first_name, c.last_name
            FROM tickets t
            LEFT JOIN customers c ON t.customer_id = c.id
            WHERE t.ticket_number = %s
        """, (ticket_number,))

        ticket = cursor.fetchone()

        if not ticket:
            flash('Ticket nicht gefunden.', 'error')
            return redirect('/')

        # Get messages (excluding internal notes)
        cursor.execute("""
            SELECT * FROM ticket_messages
            WHERE ticket_id = %s AND is_internal = FALSE
            ORDER BY created_at ASC
        """, (ticket['id'],))

        messages = cursor.fetchall()

        # Parse attachments JSON
        for message in messages:
            if message['attachments']:
                try:
                    message['attachments'] = json.loads(message['attachments'])
                except:
                    message['attachments'] = []

        cursor.close()
        conn.close()

        return render_template('ticket/view.html',
                             ticket=ticket,
                             messages=messages)

    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect('/')

# Customer views all their tickets
@ticket_bp.route('/my-tickets')
def my_tickets():
    if 'customer_id' not in session:
        flash('Bitte melden Sie sich zuerst an.', 'error')
        return redirect('/customer/login?next=/ticket/my-tickets')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get customer's tickets
        cursor.execute("""
            SELECT t.*,
                   COUNT(tm.id) as message_count,
                   MAX(tm.created_at) as last_activity
            FROM tickets t
            LEFT JOIN ticket_messages tm ON t.id = tm.ticket_id
            WHERE t.customer_id = %s
            GROUP BY t.id
            ORDER BY t.created_at DESC
        """, (session['customer_id'],))

        tickets = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('ticket/my_tickets.html', tickets=tickets)

    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect('/')

# Customer replies to their ticket
@ticket_bp.route('/reply/<ticket_number>', methods=['POST'])
def customer_reply_ticket(ticket_number):
    try:
        message = request.form.get('message', '').strip()

        if not message:
            flash('Nachricht darf nicht leer sein.', 'error')
            return redirect(url_for('ticket.view_ticket', ticket_number=ticket_number))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get ticket
        cursor.execute("SELECT * FROM tickets WHERE ticket_number = %s", (ticket_number,))
        ticket = cursor.fetchone()

        if not ticket:
            flash('Ticket nicht gefunden.', 'error')
            return redirect('/')

        # Handle file uploads
        attachments_data = []
        if 'attachments[]' in request.files:
            files = request.files.getlist('attachments[]')
            attachments_data = save_uploaded_files(files, ticket['id'], 'temp')

        # Add customer message with attachments
        cursor.execute("""
            INSERT INTO ticket_messages
            (ticket_id, sender_type, sender_id, message, attachments)
            VALUES (%s, 'customer', %s, %s, %s)
        """, (ticket['id'], ticket.get('customer_id'), message,
              json.dumps(attachments_data) if attachments_data else None))

        # Get the new message ID to rename folder
        message_id = cursor.lastrowid

        # Rename temp folder to actual message ID if needed
        if attachments_data:
            temp_dir = os.path.join(UPLOAD_FOLDER, str(ticket['id']), 'temp')
            actual_dir = os.path.join(UPLOAD_FOLDER, str(ticket['id']), str(message_id))
            if os.path.exists(temp_dir):
                os.rename(temp_dir, actual_dir)
                # Update paths in attachments
                for att in attachments_data:
                    att['path'] = f"tickets/{ticket['id']}/{message_id}/{att['filename']}"

                # Update attachments in database
                cursor.execute("""
                    UPDATE ticket_messages
                    SET attachments = %s
                    WHERE id = %s
                """, (json.dumps(attachments_data), message_id))

        # Update ticket status to waiting_customer or reopen if resolved/closed
        new_status = 'waiting_customer'
        if ticket['status'] in ['resolved', 'closed']:
            new_status = 'open'

        cursor.execute("""
            UPDATE tickets
            SET status = %s, updated_at = NOW()
            WHERE id = %s
        """, (new_status, ticket['id']))

        conn.commit()
        cursor.close()
        conn.close()

        # TODO: Send email notification to support team

        flash('✅ Ihre Antwort wurde gespeichert.', 'success')
        return redirect(url_for('ticket.view_ticket', ticket_number=ticket_number))

    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect(url_for('ticket.view_ticket', ticket_number=ticket_number))

# Admin ticket dashboard
@ticket_bp.route('/admin/dashboard')
def admin_ticket_dashboard():
    if not session.get('logged_in'):
        return redirect('/login?next=ticket/admin/dashboard')

    try:
        # Get filter parameters
        status_filter = request.args.get('status', '')
        priority_filter = request.args.get('priority', '')
        category_filter = request.args.get('category', '')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Build query
        query = """
            SELECT t.*,
                   COUNT(tm.id) as message_count,
                   MAX(tm.created_at) as last_activity
            FROM tickets t
            LEFT JOIN ticket_messages tm ON t.id = tm.ticket_id
            WHERE 1=1
        """
        params = []

        if status_filter:
            query += " AND t.status = %s"
            params.append(status_filter)
        else:
            query += " AND t.status IN ('open', 'in_progress', 'waiting_customer')"

        if priority_filter:
            query += " AND t.priority = %s"
            params.append(priority_filter)

        if category_filter:
            query += " AND t.category = %s"
            params.append(category_filter)

        query += " GROUP BY t.id ORDER BY "

        # Priority-based ordering (urgent first)
        query += """
            CASE t.priority
                WHEN 'urgent' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
                ELSE 5
            END,
            t.created_at DESC
        """

        cursor.execute(query, params)
        tickets = cursor.fetchall()

        # Get counts for stats
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'waiting_customer' THEN 1 ELSE 0 END) as waiting,
                SUM(CASE WHEN priority = 'urgent' THEN 1 ELSE 0 END) as urgent
            FROM tickets
            WHERE status IN ('open', 'in_progress', 'waiting_customer')
        """)

        stats = cursor.fetchone()

        cursor.close()
        conn.close()

        return render_template('ticket/admin_dashboard.html',
                             tickets=tickets,
                             stats=stats,
                             status_filter=status_filter,
                             priority_filter=priority_filter,
                             category_filter=category_filter)

    except Exception as e:
        return f"❌ Ticket Dashboard Fehler: {str(e)}"

# Admin views single ticket
@ticket_bp.route('/admin/ticket/<ticket_number>')
def admin_view_ticket(ticket_number):
    if not session.get('logged_in'):
        return redirect(f'/login?next=ticket/admin/ticket/{ticket_number}')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get ticket with customer info
        cursor.execute("""
            SELECT t.*, c.first_name, c.last_name, c.email, c.phone
            FROM tickets t
            LEFT JOIN customers c ON t.customer_id = c.id
            WHERE t.ticket_number = %s
        """, (ticket_number,))

        ticket = cursor.fetchone()

        if not ticket:
            flash('Ticket nicht gefunden.', 'error')
            return redirect(url_for('ticket.admin_ticket_dashboard'))

        # Get all messages (including internal notes for admin)
        cursor.execute("""
            SELECT * FROM ticket_messages
            WHERE ticket_id = %s
            ORDER BY created_at ASC
        """, (ticket['id'],))

        messages = cursor.fetchall()

        # Parse attachments JSON
        for message in messages:
            if message['attachments']:
                try:
                    message['attachments'] = json.loads(message['attachments'])
                except:
                    message['attachments'] = []

        cursor.close()
        conn.close()

        return render_template('ticket/admin_view.html',
                             ticket=ticket,
                             messages=messages)

    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect(url_for('ticket.admin_ticket_dashboard'))

# Admin replies to ticket
@ticket_bp.route('/admin/reply/<ticket_number>', methods=['POST'])
def admin_reply_ticket(ticket_number):
    if not session.get('logged_in'):
        return redirect(f'/login?next=ticket/admin/ticket/{ticket_number}')

    try:
        message = request.form.get('message', '').strip()
        is_internal = request.form.get('is_internal', '0') == '1'
        new_status = request.form.get('status', '')

        if not message:
            flash('Nachricht darf nicht leer sein.', 'error')
            return redirect(url_for('ticket.admin_view_ticket', ticket_number=ticket_number))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get ticket ID
        cursor.execute("SELECT id FROM tickets WHERE ticket_number = %s", (ticket_number,))
        ticket = cursor.fetchone()

        if not ticket:
            flash('Ticket nicht gefunden.', 'error')
            return redirect(url_for('ticket.admin_ticket_dashboard'))

        # Handle file uploads
        attachments_data = []
        if 'attachments[]' in request.files:
            files = request.files.getlist('attachments[]')
            attachments_data = save_uploaded_files(files, ticket['id'], 'temp')

        # Add admin message with attachments
        cursor.execute("""
            INSERT INTO ticket_messages
            (ticket_id, sender_type, sender_id, message, is_internal, attachments)
            VALUES (%s, 'admin', %s, %s, %s, %s)
        """, (ticket['id'], 1, message, is_internal,
              json.dumps(attachments_data) if attachments_data else None))

        # Get the new message ID to rename folder
        message_id = cursor.lastrowid

        # Rename temp folder to actual message ID if needed
        if attachments_data:
            temp_dir = os.path.join(UPLOAD_FOLDER, str(ticket['id']), 'temp')
            actual_dir = os.path.join(UPLOAD_FOLDER, str(ticket['id']), str(message_id))
            if os.path.exists(temp_dir):
                os.rename(temp_dir, actual_dir)
                # Update paths in attachments
                for att in attachments_data:
                    att['path'] = f"tickets/{ticket['id']}/{message_id}/{att['filename']}"

                # Update attachments in database
                cursor.execute("""
                    UPDATE ticket_messages
                    SET attachments = %s
                    WHERE id = %s
                """, (json.dumps(attachments_data), message_id))

        # Update ticket status if changed
        if new_status and new_status in ['open', 'in_progress', 'waiting_customer', 'resolved', 'closed']:
            cursor.execute("""
                UPDATE tickets
                SET status = %s, updated_at = NOW()
                WHERE id = %s
            """, (new_status, ticket['id']))

            if new_status in ['resolved', 'closed']:
                cursor.execute("""
                    UPDATE tickets
                    SET closed_at = NOW()
                    WHERE id = %s AND closed_at IS NULL
                """, (ticket['id'],))

        conn.commit()
        cursor.close()
        conn.close()

        # TODO: Send email notification to customer if not internal

        flash('✅ Antwort wurde gespeichert.', 'success')
        return redirect(url_for('ticket.admin_view_ticket', ticket_number=ticket_number))

    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect(url_for('ticket.admin_view_ticket', ticket_number=ticket_number))
