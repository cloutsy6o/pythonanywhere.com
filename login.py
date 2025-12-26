from flask import Flask, render_template, request, session, redirect
import bcrypt

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Hardcoded user (from your PHP)
USER = "username"
HASH = 'password'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        next_page = request.form.get('next', 'admin_view_hotels')

        if username == USER and bcrypt.checkpw(password.encode('utf-8'), HASH.encode('utf-8')):
            session['logged_in'] = True
            return redirect(f'/{next_page}')
        else:
            error = "Falscher Benutzername oder Passwort."
            return render_template('login.html', error=error, next=request.form.get('next', ''))

    return render_template('login.html', next=request.args.get('next', ''))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
