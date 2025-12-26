from flask import session, redirect

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
