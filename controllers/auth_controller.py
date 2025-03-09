import hashlib
from flask import request, redirect, url_for, session,render_template
from config import get_dashboard_conf


def signin():
    message = ""
    if "message" in session:
        message = session['message']
        session.pop("message")
    return render_template('signin.html', message=message)

def signout():
    if "username" in session:
        session.pop("username")
    message = "Sign out successfully!"
    return render_template('signin.html', message=message)
def auth():
    config = get_dashboard_conf()
    password = hashlib.sha256(request.form['password'].encode())
    if password.hexdigest() == config["Account"]["password"] and request.form['username'] == config["Account"][
        "username"]:
        session['username'] = request.form['username']
        return redirect(url_for("dashboard_views.index_route"))
    else:
        session['message'] = "Username or Password is incorrect."
        return redirect(url_for("auth_views.signin_route"))