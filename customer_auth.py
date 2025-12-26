from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from flask_bcrypt import Bcrypt
from functools import wraps
from db import get_db_connection
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

def get_serializer():
    from app import app
    return URLSafeTimedSerializer(app.secret_key)

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

# Helper: Check if customer is logged in
def customer_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_id' not in session:
            flash('Bitte melden Sie sich zuerst an.', 'warning')
            return redirect(url_for('customer.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ----- CUSTOMER REGISTRATION -----
@customer_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('customer/register.html')

    try:
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        # Validation
        if not email or not password:
            flash('E-Mail und Passwort sind erforderlich.', 'error')
            return redirect(url_for('customer.register'))

        if password != confirm_password:
            flash('Passwörter stimmen nicht überein.', 'error')
            return redirect(url_for('customer.register'))

        if len(password) < 6:
            flash('Passwort muss mindestens 6 Zeichen lang sein.', 'error')
            return redirect(url_for('customer.register'))

        conn = get_db_connection()
        if not conn:
            flash('Datenbankverbindungsfehler.', 'error')
            return redirect(url_for('customer.register'))

        cursor = conn.cursor(dictionary=True)

        # Check if email exists
        cursor.execute("SELECT id FROM customers WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash('E-Mail bereits registriert.', 'error')
            return redirect(url_for('customer.register'))

        # Hash password
        from app import bcrypt
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Generate verification token
        serializer = get_serializer()
        verification_token = serializer.dumps(email, salt='email-verification')

        # Insert customer WITH verification
        cursor.execute("""
            INSERT INTO customers (email, password_hash, first_name, last_name,
                                  verification_token, email_verified)
            VALUES (%s, %s, %s, %s, %s, TRUE)
        """, (email, password_hash, first_name, last_name, verification_token))

        customer_id = cursor.lastrowid

        # FAKE EMAIL SENDING (prints to console)
        verification_url = url_for('customer.verify_email', token=verification_token, _external=True)
        print(f"[DEV EMAIL] Verification link for {email}: {verification_url}")

        conn.commit()
        cursor.close()
        conn.close()

        flash('Registrierung erfolgreich! Bitte überprüfen Sie Ihre E-Mails zur Bestätigung.', 'success')
        return redirect(url_for('customer.login'))

    except Exception as e:
        flash(f'Fehler bei der Registrierung: {str(e)}', 'error')
        return redirect(url_for('customer.register'))

# ----- EMAIL VERIFICATION -----
@customer_bp.route('/verify/<token>')
def verify_email(token):
    try:
        serializer = get_serializer()
        email = serializer.loads(token, salt='email-verification', max_age=86400)  # 24 hours

        conn = get_db_connection()
        if not conn:
            return render_template('customer/verify_email.html',
                                 success=False,
                                 message="Datenbankverbindungsfehler.")

        cursor = conn.cursor()

        cursor.execute("""
            UPDATE customers
            SET email_verified = TRUE, verification_token = NULL
            WHERE email = %s AND verification_token = %s
        """, (email, token))

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return render_template('customer/verify_email.html',
                                 success=False,
                                 message="Ungültiger oder abgelaufener Bestätigungslink.")

        conn.commit()
        cursor.close()
        conn.close()

        return render_template('customer/verify_email.html',
                             success=True,
                             message="E-Mail erfolgreich bestätigt! Sie können sich jetzt anmelden.")

    except SignatureExpired:
        return render_template('customer/verify_email.html',
                             success=False,
                             message="Bestätigungslink ist abgelaufen. Bitte registrieren Sie sich erneut.")
    except BadSignature:
        return render_template('customer/verify_email.html',
                             success=False,
                             message="Ungültiger Bestätigungslink.")
    except Exception as e:
        return render_template('customer/verify_email.html',
                             success=False,
                             message=f"Fehler: {str(e)}")

# ----- CUSTOMER LOGIN -----
@customer_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('customer/login.html')

    try:
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('E-Mail und Passwort sind erforderlich.', 'error')
            return redirect(url_for('customer.login'))

        conn = get_db_connection()
        if not conn:
            flash('Datenbankverbindungsfehler.', 'error')
            return redirect(url_for('customer.login'))

        cursor = conn.cursor(dictionary=True)

        # Get customer
        cursor.execute("""
            SELECT id, email, password_hash, first_name, last_name, email_verified, is_active
            FROM customers
            WHERE email = %s
        """, (email,))

        customer = cursor.fetchone()

        if not customer:
            cursor.close()
            conn.close()
            flash('Ungültige E-Mail oder Passwort.', 'error')
            return redirect(url_for('customer.login'))

        # Verify password
        from app import bcrypt
        if not bcrypt.check_password_hash(customer['password_hash'], password):
            cursor.close()
            conn.close()
            flash('Ungültige E-Mail oder Passwort.', 'error')
            return redirect(url_for('customer.login'))

        # Check if email is verified
        if not customer['email_verified']:
            cursor.close()
            conn.close()
            flash('Bitte bestätigen Sie zuerst Ihre E-Mail.', 'error')
            return redirect(url_for('customer.login'))

        # Check if account is active
        if not customer['is_active']:
            cursor.close()
            conn.close()
            flash('Konto ist deaktiviert.', 'error')
            return redirect(url_for('customer.login'))

        # Update last login
        cursor.execute("""
            UPDATE customers
            SET last_login = NOW()
            WHERE id = %s
        """, (customer['id'],))

        # Create customer session
        session['customer_id'] = customer['id']
        session['customer_email'] = customer['email']
        session['customer_name'] = f"{customer['first_name'] or ''} {customer['last_name'] or ''}".strip()
        session['user_type'] = 'customer'

        conn.commit()
        cursor.close()
        conn.close()

        flash('Login erfolgreich!', 'success')

        # Redirect to next page or home
        next_page = request.args.get('next')
        return redirect(next_page or url_for('startseite'))

    except Exception as e:
        flash(f'Login-Fehler: {str(e)}', 'error')
        return redirect(url_for('customer.login'))

# ----- CUSTOMER LOGOUT -----
@customer_bp.route('/logout')
def logout():
    session.pop('customer_id', None)
    session.pop('customer_email', None)
    session.pop('customer_name', None)
    session.pop('user_type', None)
    flash('Erfolgreich abgemeldet.', 'success')
    return redirect(url_for('customer.login'))

# ----- CUSTOMER PROFILE -----
@customer_bp.route('/profile')
@customer_login_required
def profile():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT email, first_name, last_name, address, city,
                   zip_code, country, phone, created_at, last_login
            FROM customers
            WHERE id = %s
        """, (session['customer_id'],))

        customer = cursor.fetchone()
        cursor.close()
        conn.close()

        return render_template('customer/profile.html', customer=customer)

    except Exception as e:
        flash(f'Fehler beim Laden des Profils: {str(e)}', 'error')
        return redirect(url_for('startseite'))

# ----- SIMPLE TEMPLATE RENDERING -----
@customer_bp.route('/forgot-password')
def forgot_password():
    return render_template('customer/forgot_password.html')

@customer_bp.route('/reset-password')
def reset_password():
    return "Password reset will be implemented later"
