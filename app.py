# app.py

from flask import Flask, request, session
from flask_qrcode import QRcode
import secrets
from config import get_dashboard_conf, DASHBOARD_VERSION, init_dashboard_config
from flask import Flask, request, session, redirect, url_for 
# Import các Blueprint
from views.dashboard_views import dashboard_views
from views.config_views import config_views
from views.settings_views import settings_views
from views.auth_views import auth_views
from views.peer_views import peer_views

app = Flask("WGDashboard")
app.secret_key = secrets.token_urlsafe(16)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Tự động reload template khi thay đổi
QRcode(app)

# Register các Blueprint
app.register_blueprint(dashboard_views)
app.register_blueprint(config_views)
app.register_blueprint(settings_views)
app.register_blueprint(auth_views)
app.register_blueprint(peer_views)
# Before request (xử lý xác thực)
@app.before_request
def auth_req():
    config = get_dashboard_conf()
    req = config.get("Server", "auth_req")
    session['update'] = ""  # Bạn cần định nghĩa biến update
    session['dashboard_version'] = DASHBOARD_VERSION
    if req == "true":
        if '/static/' not in request.path and \
                request.endpoint != "auth_views.signin_route" and \
                request.endpoint != "auth_views.signout_route" and \
                request.endpoint != "auth_views.auth_route" and \
                "username" not in session:
            print("User not loggedin - Attemped access: " + str(request.endpoint))
            if request.endpoint != "dashboard_views.index":
                session['message'] = "You need to sign in first!"
            else:
                session['message'] = ""
            return redirect(url_for("auth_views.signin_route")) 
    else:
        if request.endpoint in ['auth_views.signin_route', 'auth_views.signout_route', 'auth_views.auth_route', 'settings_views.settings', 'settings_views.update_acct_route', 'settings_views.update_pwd_route',
                                'settings_views.update_app_ip_port_route', 'settings_views.update_wg_conf_path_route']:
            return redirect(url_for("dashboard_views.index_route"))


if __name__ == "__main__":
    init_dashboard_config()  
    config = get_dashboard_conf()
    app_ip = config.get("Server", "app_ip")
    app_port = config.get("Server", "app_port")
    app.run(host=app_ip, debug=False, port=app_port)