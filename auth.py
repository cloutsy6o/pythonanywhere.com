from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import bcrypt
from db import get_db_connection

auth_bp = Blueprint('auth', __name__)

# Hardcoded user for now (from your PHP)
USER = "username"
HASH = 'password'

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        next_page = request.form.get('next', 'admin_view_hotels')

        if username == USER and bcrypt.checkpw(password.encode('utf-8'), HASH.encode('utf-8')):
            session['logged_in'] = True
            return redirect(url_for(next_page))
        else:
            flash('Falscher Benutzername oder Passwort.', 'error')

    return render_template('login.html', next=request.args.get('next', ''))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
