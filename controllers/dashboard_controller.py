# controllers/dashboard_controller.py
from flask import render_template, request, redirect, url_for, session, jsonify
from models.wireguard_model import get_conf_list, get_conf_status, get_conf_total_data, switch_interface
from models.dashboard_model import get_peers, get_peer_data, update_peer_data, add_peer, remove_peer
from config import get_dashboard_conf, set_dashboard_conf
import urllib.parse
from models import  regex_match, check_IP_with_range, check_DNS, check_Allowed_IPs, check_remote_endpoint
from models.wireguard_model import *
import hashlib 
import ifcfg 
def index():
    config = get_dashboard_conf()
    wg_conf_path = config.get("Server", "wg_conf_path")
    return render_template('index.html', conf=get_conf_list(wg_conf_path))

def configuration(config_name):
    # ... (Code xử lý cho trang configuration) ...
    config = get_dashboard_conf()
    wg_conf_path = config.get("Server", "wg_conf_path")
    conf_data = {
        "name": config_name,
        "status": get_conf_status(config_name),
        "checked": ""
    }
    if conf_data['status'] == "stopped":
        conf_data['checked'] = "nope"
    else:
        conf_data['checked'] = "checked"
    config_list = get_conf_list(wg_conf_path)
    if config_name not in [conf['conf'] for conf in config_list]:
        return render_template('index.html', conf=get_conf_list(wg_conf_path))
    print(conf_data)
    return render_template('configuration.html', conf=get_conf_list(wg_conf_path), conf_data=conf_data,
                        dashboard_refresh_interval=int(config.get("Server", "dashboard_refresh_interval")),
                        DNS=config.get("Peers", "peer_global_DNS"),
                        endpoint_allowed_ip=config.get("Peers", "peer_endpoint_allowed_ip"),
                        title=config_name,
                        mtu=config.get("Peers","peer_MTU"),
                        keep_alive=config.get("Peers","peer_keep_alive"))

def get_config(config_name):
    # ... (Code xử lý để lấy thông tin config) ...
    config = get_dashboard_conf()
    search = request.args.get('search', '')
    search = urllib.parse.unquote(search)

    sort = config.get("Server", "dashboard_sort")
    peer_display_mode = config.get("Peers", "peer_display_mode")
    conf_address = "N/A" # Giá trị mặc định

    interface_data = read_conf_file_interface(config_name, config.get("Server", "wg_conf_path"))

    if "Address" in interface_data:
        conf_address = interface_data['Address']
    wg_conf_path = config.get("Server", "wg_conf_path")
    conf_data = {
        "peer_data": get_peers(config_name, search, sort),
        "name": config_name,
        "status": get_conf_status(config_name),
        "total_data_usage": get_conf_total_data(config_name),
        "public_key": get_conf_pub_key(config_name, wg_conf_path),
        "listen_port": get_conf_listen_port(config_name, wg_conf_path),
        "running_peer": get_conf_running_peer_number(config_name),
        "conf_address": conf_address
    }
    if conf_data['status'] == "stopped":
        conf_data['checked'] = "nope"
    else:
        conf_data['checked'] = "checked"
    return render_template('get_conf.html', conf_data=conf_data, wg_ip=config.get("Peers","remote_endpoint"), sort_tag=sort,
                        dashboard_refresh_interval=int(config.get("Server", "dashboard_refresh_interval")), peer_display_mode=peer_display_mode)

def switch(config_name):
    # ... (Code xử lý bật/tắt interface) ...

    if "username" not in session:
        print("not loggedin")
        return redirect(url_for("signin")) # Nên dùng url_for từ auth_views
    status = get_conf_status(config_name,interfaces=dict(ifcfg.interfaces().items()))
    if status == "running":
        operation = "down"
    elif status == "stopped":
        operation = "up"
    else:
        return redirect('/') # Hoặc xử lý lỗi khác

    result = switch_interface(config_name, operation)
    if result == "failed":
        return redirect('/')  # Hoặc xử lý lỗi

    return redirect(request.referrer)
def add_peer_controller(config_name):
    # ...
    config = get_dashboard_conf()
    wg_conf_path = config.get("Server", "wg_conf_path")
    data = request.get_json()
    # ... (Kiểm tra dữ liệu đầu vào) ...
    if len(data['public_key']) == 0 or len(data['DNS']) == 0 or len(data['allowed_ips']) == 0 or len(data['endpoint_allowed_ip']) == 0:
        return "Please fill in all required box."
    if data['public_key'] in get_conf_peer_key(config_name):
        return "Public key already exist."
    if not check_DNS(data['DNS']):
        return "DNS formate is incorrect. Example: 1.1.1.1"
    if not check_Allowed_IPs(data['endpoint_allowed_ip']):
        return "Endpoint Allowed IPs format is incorrect."
    if len(data['MTU']) != 0:
        try:
            mtu = int(data['MTU'])
        except:
            return "MTU format is not correct."
    if len(data['keep_alive']) != 0:
        try:
            keep_alive = int(data['keep_alive'])
        except:
            return "Persistent Keepalive format is not correct."
        
    result = add_peer_to_conf(config_name, data['public_key'], data['allowed_ips'], wg_conf_path)
    if result != "true":
        return result  # Trả về thông báo lỗi nếu có
    get_all_peers_data(config_name)
    # Thêm peer vào database (model)
    success, message = add_peer(config_name, data)
    if not success:
        return message

    # Thêm peer vào file config (model)

    return "true"
def remove_peer_controller(config_name):
    # ...
    data = request.get_json()
    delete_key = data['peer_id']
    config = get_dashboard_conf()
    wg_conf_path = config.get("Server", "wg_conf_path")
    if get_conf_status(config_name) == "stopped":
        return "Your need to turn on " + config_name + " first."

    if delete_key not in get_conf_peer_key(config_name):
        return "This key does not exist"
    # Xóa peer từ file config (model)
    result = remove_peer_from_conf(config_name, delete_key, wg_conf_path)

    if result != "true":
        return result

    # Xóa peer từ database (model)
    remove_peer(config_name, delete_key) # Không cần kiểm tra, vì đã kiểm tra key tồn tại ở trên
    return "true"
def save_peer_setting(config_name):
    # ...
    data = request.get_json()
    peer_id = data['id']

    # Kiểm tra dữ liệu
    if not check_IP_with_range(data['endpoint_allowed_ip']):
        return jsonify({"status": "failed", "msg": "Endpoint Allowed IPs format is incorrect."})
    if not check_DNS(data['DNS']):
        return jsonify({"status": "failed", "msg": "DNS format is incorrect."})
    if len(data['MTU']) != 0:
        try:
            mtu = int(data['MTU'])
        except:
            return jsonify({"status": "failed", "msg": "MTU format is not correct."})
    if len(data['keep_alive']) != 0:
        try:
            keep_alive = int(data['keep_alive'])
        except:
            return jsonify({"status": "failed", "msg": "Persistent Keepalive format is not correct."})

    if data['private_key'] != "":
        check_key = check_key_match(data['private_key'], peer_id, config_name)
        if check_key['status'] == "failed":
            return jsonify(check_key)

    check_ip = check_repeat_allowed_IP(peer_id, data['allowed_ip'], config_name)
    if check_ip['status'] == "failed":
        return jsonify(check_ip)

    # Cập nhật allowed IPs trong file config (model)
    success, message = update_peer_allowed_ips(config_name, peer_id, data['allowed_ip'])
    if not success:
        return jsonify({"status": "failed", "msg": message})

    # Cập nhật database (model)
    if update_peer_data(config_name, peer_id, data):
         return jsonify({"status": "success", "msg": ""})
    else:
        return jsonify({"status": "failed", "msg": "This peer does not exist."})


def get_peer_data_controller(config_name):
    # ...
    data = request.get_json()
    peer_id = data['id']
    peer_data = get_peer_data(config_name, peer_id)
    if peer_data:
        return jsonify(peer_data)
    else:
        return jsonify({"error": "Peer not found"}), 404  # Trả về 404 nếu không tìm thấy

def generate_peer():
    # ...
    return jsonify(gen_private_key())

def generate_public_key():
    # ...
    data = request.get_json()
    private_key = data['private_key']
    return jsonify(gen_public_key(private_key))

def check_key_match_controller(config_name):
    # ...
    data = request.get_json()
    private_key = data['private_key']
    public_key = data['public_key']
    return jsonify(check_key_match(private_key, public_key, config_name))

def download(config_name):
    # ...
    config = get_dashboard_conf()
    wg_conf_path = config.get("Server", "wg_conf_path")
    remote_endpoint = config.get("Peers","remote_endpoint")
    peer_id = request.args.get('id')
    config_content, filename = generate_peer_config(config_name, peer_id, wg_conf_path, remote_endpoint)

    if config_content is None:
        return redirect(url_for("config_views.configuration", config_name=config_name))  # Chuyển hướng nếu lỗi

    response = make_response(config_content)
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}.conf"'
    response.headers['Content-Type'] = 'text/plain'  # Đặt đúng Content-Type
    return response
def create_client(config_name):
    # ...
    data = request.get_json()
    config = get_dashboard_conf()
    wg_conf_path = config.get("Server", "wg_conf_path")
    default_dns = config.get("Peers", "peer_global_DNS")
    default_endpoint_allowed_ip = config.get("Peers", "peer_endpoint_allowed_ip")
    base_ip = BASE_IP  # Import từ config
    remote_endpoint = config.get("Peers", "remote_endpoint")
    config_content, error = create_client_config(config_name, data, wg_conf_path, default_dns, default_endpoint_allowed_ip, base_ip, remote_endpoint)

    if error:
        return jsonify({"error": error}), 409

    response = make_response(config_content)
    response.headers['Content-Disposition'] = f'attachment; filename="{data["name"]}_wg.conf"'
    return response