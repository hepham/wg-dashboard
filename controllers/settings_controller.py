from flask import render_template, request, redirect, url_for, session, jsonify
from config import get_dashboard_conf, set_dashboard_conf
from models import check_DNS, check_Allowed_IPs, check_remote_endpoint
from models.wireguard_model import *
import hashlib 
def settings():

    message = ""
    status = ""
    config = get_dashboard_conf()
    if "message" in session and "message_status" in session:
        message = session['message']
        status = session['message_status']
        session.pop("message")
        session.pop("message_status")
    required_auth = config.get("Server", "auth_req")
    return render_template('settings.html', conf=get_conf_list(config.get("Server", "wg_conf_path")), message=message, status=status,
                          app_ip=config.get("Server", "app_ip"), app_port=config.get("Server", "app_port"),
                          required_auth=required_auth, wg_conf_path=config.get("Server", "wg_conf_path"),
                          peer_global_DNS=config.get("Peers", "peer_global_DNS"),
                          peer_endpoint_allowed_ip=config.get("Peers", "peer_endpoint_allowed_ip"),
                          peer_mtu=config.get("Peers", "peer_mtu"),
                          peer_keepalive=config.get("Peers","peer_keep_alive"),
                          peer_remote_endpoint=config.get("Peers","remote_endpoint"))
def update_account():
    
    if len(request.form['username']) == 0:
        session['message'] = "Username cannot be empty."
        session['message_status'] = "danger"
        return redirect(url_for("settings_views.settings")) 
    config = get_dashboard_conf()
    config.set("Account", "username", request.form['username'])
    try:
        set_dashboard_conf(config)  # Dùng hàm set_dashboard_conf
        session['message'] = "Username update successfully!"
        session['message_status'] = "success"
        session['username'] = request.form['username']
        return redirect(url_for("settings_views.settings_route")) 
    except Exception:
        session['message'] = "Username update failed."
        session['message_status'] = "danger"
        return redirect(url_for("settings_views.settings_route")) 
def update_peer_default():

    config = get_dashboard_conf()
    if len(request.form['peer_endpoint_allowed_ip']) == 0 or \
            len(request.form['peer_global_DNS']) == 0 or \
            len(request.form['peer_remote_endpoint']) == 0:
        session['message'] = "Please fill in all required boxes."
        session['message_status'] = "danger"
        return redirect(url_for("settings_views.settings_route")) 
    # Check DNS Format
    DNS = request.form['peer_global_DNS']
    if not check_DNS(DNS):
        session['message'] = "Peer DNS Format Incorrect."
        session['message_status'] = "danger"
        return redirect(url_for("settings_views.settings_route")) 
    DNS = DNS.replace(" ","").split(',')
    DNS = ",".join(DNS)

    # Check Endpoint Allowed IPs
    ip = request.form['peer_endpoint_allowed_ip']
    if not check_Allowed_IPs(ip):
        session['message'] = "Peer Endpoint Allowed IPs Format Incorrect. Example: 192.168.1.1/32 or 192.168.1.1/32,192.168.1.2/32"
        session['message_status'] = "danger"
        return redirect(url_for("settings_views.settings_route")) 
    # Check MTU Format
    if len(request.form['peer_mtu']) > 0:
        try:
            mtu = int(request.form['peer_mtu'])
        except:
            session['message'] = "MTU format is incorrect."
            session['message_status'] = "danger"
            return redirect(url_for("settings_views.settings_route")) 
    # Check keepalive Format
    if len(request.form['peer_keep_alive']) > 0:
        try:
            mtu = int(request.form['peer_keep_alive'])
        except:
            session['message'] = "Persistent keepalive format is incorrect."
            session['message_status'] = "danger"
            return redirect(url_for("settings_views.settings_route")) 
    # Check peer remote endpoint
    if not check_remote_endpoint(request.form['peer_remote_endpoint']):
        session[
            'message'] = "Peer Remote Endpoint format is incorrect. It can only be a valid IP address or valid domain (without http:// or https://). "
        session['message_status'] = "danger"
        return redirect(url_for("settings_views.settings_route")) 

    config.set("Peers", "remote_endpoint", request.form['peer_remote_endpoint'])
    config.set("Peers", "peer_keep_alive", request.form['peer_keep_alive'])
    config.set("Peers", "peer_mtu", request.form['peer_mtu'])
    config.set("Peers", "peer_endpoint_allowed_ip", ','.join(models.clean_IP_with_range(ip)))
    config.set("Peers", "peer_global_DNS", DNS)
    try:
        set_dashboard_conf(config)
        session['message'] = "Peer Default Settings update successfully!"
        session['message_status'] = "success"
        return redirect(url_for("settings_views.settings_route")) 
    except Exception:
        session['message'] = "Peer Default Settings update failed."
        session['message_status'] = "danger"
        return redirect(url_for("settings_views.settings_route"))

def update_password():

    config = get_dashboard_conf()
    if hashlib.sha256(request.form['currentpass'].encode()).hexdigest() == config.get("Account", "password"):
        if hashlib.sha256(request.form['newpass'].encode()).hexdigest() == hashlib.sha256(
                request.form['repnewpass'].encode()).hexdigest():
            config.set("Account", "password", hashlib.sha256(request.form['repnewpass'].encode()).hexdigest())
            try:
                set_dashboard_conf(config)
                session['message'] = "Password update successfully!"
                session['message_status'] = "success"
                return redirect(url_for("settings_views.settings_route")) 
            except Exception:
                session['message'] = "Password update failed"
                session['message_status'] = "danger"
                return redirect(url_for("settings_views.settings_route")) 
        else:
            session['message'] = "Your New Password does not match."
            session['message_status'] = "danger"
            return redirect(url_for("settings_views.settings_route")) 
    else:
        session['message'] = "Your Password does not match."
        session['message_status'] = "danger"
        return redirect(url_for("settings_views.settings_route")) 
def update_app_ip_port():

    config = get_dashboard_conf()
    config.set("Server", "app_ip", request.form['app_ip'])
    config.set("Server", "app_port", request.form['app_port'])
    set_dashboard_conf(config)
    os.system('bash wgd.sh restart') # Cái này có thể gây vấn đề bảo mật, xem xét dùng subprocess
def update_wg_conf_path():

    config = get_dashboard_conf()
    config.set("Server", "wg_conf_path", request.form['wg_conf_path'])
    set_dashboard_conf(config)
    session['message'] = "WireGuard Configuration Path Update Successfully!"
    session['message_status'] = "success"
    os.system('bash wgd.sh restart')
def update_dashboard_sort():

    config = get_dashboard_conf()
    data = request.get_json()
    sort_tag = ['name', 'status', 'allowed_ip']
    if data['sort'] in sort_tag:
        config.set("Server", "dashboard_sort", data['sort'])
    else:
        config.set("Server", "dashboard_sort", 'status')
    set_dashboard_conf(config)
    return "true"
def update_dashboard_refresh_interval():

    config = get_dashboard_conf()
    config.set("Server", "dashboard_refresh_interval", str(request.form['interval']))
    set_dashboard_conf(config)
    return "true"
def switch_display_mode(mode):

    if mode in ['list','grid']:
        config = get_dashboard_conf() # Sửa lại đây, cần lấy config
        config.set("Peers", "peer_display_mode", mode)
        set_dashboard_conf(config)
        return "true"
    else:
        return "false"
