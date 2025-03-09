# models/wireguard_model.py

import subprocess
import re
import configparser
from datetime import datetime, timedelta
from tinydb import TinyDB, Query
import os
from . import regex_match, check_IP_with_range, check_DNS, check_Allowed_IPs, check_remote_endpoint
from config import BASE_IP
import ifcfg
from operator import itemgetter
def read_conf_file_interface(config_name, wg_conf_path):
    # ... (Code của bạn) ...
    conf_location = wg_conf_path + "/" + config_name + ".conf"
    f = open(conf_location, 'r')
    file = f.read().split("\n")
    data = {}
    peers_start = 0
    for i in range(len(file)):
        if not regex_match("#(.*)", file[i]):
            if len(file[i]) > 0:
                if file[i] != "[Interface]":
                    tmp = re.split(r'\s*=\s*', file[i], 1)
                    if len(tmp) == 2:
                        data[tmp[0]] = tmp[1]
    f.close()
    return data


def read_conf_file(config_name, wg_conf_path):
    # ... (Code của bạn) ...
    conf_location = wg_conf_path + "/" + config_name + ".conf"
    f = open(conf_location, 'r')
    file = f.read().split("\n")

    # Parse thành dict chứa Interface và Peers
    conf_peer_data = {
        "Interface": {},
        "Peers": []
    }
    peers_start = 0
    for i in range(len(file)):
        if not regex_match("#(.*)", file[i]):
            if file[i] == "[Peer]":
                peers_start = i
                break
            else:
                if len(file[i]) > 0:
                    if file[i] != "[Interface]":
                        tmp = re.split(r'\s*=\s*', file[i], 1)
                        if len(tmp) == 2:
                            conf_peer_data['Interface'][tmp[0]] = tmp[1]
    conf_peers = file[peers_start:]
    peer = -1
    for i in conf_peers:
        if not regex_match("#(.*)", i):
            if i == "[Peer]":
                peer += 1
                conf_peer_data["Peers"].append({})
            elif peer > -1:
                if len(i) > 0:
                    tmp = re.split('\s*=\s*', i, 1)
                    if len(tmp) == 2:
                        conf_peer_data["Peers"][peer][tmp[0]] = tmp[1]

    f.close()
    return conf_peer_data

def get_conf_peer_key(config_name):
    # ...
    try:
        peer_key = subprocess.check_output("wg show " + config_name + " peers", shell=True)
        peer_key = peer_key.decode("UTF-8").split()
        return peer_key
    except Exception:
        return config_name + " is not running."

def get_conf_running_peer_number(config_name):
    # ...
    running = 0
    # Get latest handshakes
    try:
        data_usage = subprocess.check_output("wg show " + config_name + " latest-handshakes", shell=True)
    except Exception:
        return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    now = datetime.now()
    b = timedelta(minutes=2)
    for i in range(int(len(data_usage) / 2)):
        minus = now - datetime.fromtimestamp(int(data_usage[count + 1]))
        if minus < b:
            running += 1
        count += 2
    return running
def get_latest_handshake(config_name, db, peers):
    # ...
    # Get latest handshakes
    try:
        data_usage = subprocess.check_output("wg show " + config_name + " latest-handshakes", shell=True)
    except Exception:
        return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    now = datetime.now()
    b = timedelta(minutes=2)
    for i in range(int(len(data_usage) / 2)):
        minus = now - datetime.fromtimestamp(int(data_usage[count + 1]))
        if minus < b:
            status = "running"
        else:
            status = "stopped"
        if int(data_usage[count + 1]) > 0:
            db.update({"latest_handshake": str(minus).split(".")[0], "status": status},
                    peers.id == data_usage[count])
        else:
            db.update({"latest_handshake": "(None)", "status": status}, peers.id == data_usage[count])
        count += 2

def get_transfer(config_name, db, peers):
    # ...
    try:
        data_usage = subprocess.check_output("wg show " + config_name + " transfer", shell=True)
    except Exception:
        return "stopped"

    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    for i in range(int(len(data_usage) / 3)):
        cur_i = db.search(peers.id == data_usage[count])

        # Kiểm tra và khởi tạo giá trị mặc định
        total_sent = cur_i[0].get('total_sent', 0)  # Sử dụng get để lấy giá trị hoặc 0 nếu không tồn tại
        total_receive = cur_i[0].get('total_receive', 0)  # Tương tự cho total_receive
        traffic = cur_i[0].get('traffic', [])  # Khởi tạo traffic là danh sách rỗng nếu không tồn tại

        cur_total_sent = round(int(data_usage[count + 2]) / (1024 ** 3), 4)
        cur_total_receive = round(int(data_usage[count + 1]) / (1024 ** 3), 4)

        if cur_i[0]["status"] == "running":
            if total_sent <= cur_total_sent and total_receive <= cur_total_receive:
                total_sent = cur_total_sent
                total_receive = cur_total_receive
            else:
                now = datetime.now()
                ctime = now.strftime("%d/%m/%Y %H:%M:%S")
                traffic.append({
                    "time": ctime,
                    "total_receive": round(total_receive, 4),
                    "total_sent": round(total_sent, 4),
                    "total_data": round(total_receive + total_sent, 4)
                })
                total_sent = 0
                total_receive = 0

            db.update({
                "traffic": traffic,
                "total_receive": round(total_receive, 4),
                "total_sent": round(total_sent, 4),
                "total_data": round(total_receive + total_sent, 4)
            }, peers.id == data_usage[count])

        count += 3

def get_endpoint(config_name, db, peers):
    # ...
    try:
        data_usage = subprocess.check_output("wg show " + config_name + " endpoints", shell=True)
    except Exception:
        return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    for i in range(int(len(data_usage) / 2)):
        db.update({"endpoint": data_usage[count + 1]}, peers.id == data_usage[count])
        count += 2
def get_allowed_ip(config_name, db, peers, conf_peer_data):
    # ...
    for i in conf_peer_data["Peers"]:
        db.update({"allowed_ip": i.get('AllowedIPs', '(None)')}, peers.id == i["PublicKey"])

def get_all_peers_data(config_name, wg_conf_path, peer_global_DNS, peer_endpoint_allowed_ip, peer_mtu,peer_keep_alive,remote_endpoint):
    # ...
    db = TinyDB('db/' + config_name + '.json')
    peers = Query()
    conf_peer_data = read_conf_file(config_name,wg_conf_path)
    # config = get_dashboard_conf() # Không cần thiết vì đã truyền các giá trị config
    for i in conf_peer_data['Peers']:
        search = db.search(peers.id == i['PublicKey'])
        if not search:
            db.insert({
                "id": i['PublicKey'],
                "private_key": "",
                "DNS": peer_global_DNS,
                "endpoint_allowed_ip": peer_endpoint_allowed_ip,
                "name": "",
                "total_receive": 0,
                "total_sent": 0,
                "total_data": 0,
                "endpoint": "N/A",
                "status": "stopped",
                "latest_handshake": "N/A",
                "allowed_ip": "N/A",
                "traffic": [],
                "mtu": peer_mtu,
                "keepalive": peer_keep_alive,
                "remote_endpoint":remote_endpoint
            })
        else:
            # Update database since V2.2
            update_db = {}
            # Required peer settings
            if "DNS" not in search[0]:
                update_db['DNS'] = peer_global_DNS
            if "endpoint_allowed_ip" not in search[0]:
                update_db['endpoint_allowed_ip'] = peer_endpoint_allowed_ip
            # Not required peers settings (Only for QR code)
            if "private_key" not in search[0]:
                update_db['private_key'] = ''
            if "mtu" not in search[0]:
                update_db['mtu'] = peer_mtu
            if "keepalive" not in search[0]:
                update_db['keepalive'] = peer_keep_alive
            if "remote_endpoint" not in search[0]:
                update_db['remote_endpoint'] = remote_endpoint
            db.update(update_db, peers.id == i['PublicKey'])
    # Remove peers no longer exist in WireGuard configuration file
    db_key = list(map(lambda a: a['id'], db.all()))
    wg_key = list(map(lambda a: a['PublicKey'], conf_peer_data['Peers']))
    for i in db_key:
        if i not in wg_key:
            db.remove(peers.id == i)
    # Removed time tracking
    get_latest_handshake(config_name, db, peers)
    get_transfer(config_name, db, peers)
    get_endpoint(config_name, db, peers)
    get_allowed_ip(config_name, db, peers, conf_peer_data)

    db.close()
def get_conf_pub_key(config_name, wg_conf_path):
    # ...
    conf = configparser.ConfigParser(strict=False)
    conf.read(wg_conf_path + "/" + config_name + ".conf")
    pri = conf.get("Interface", "PrivateKey")
    pub = subprocess.check_output("echo '" + pri + "' | wg pubkey", shell=True)
    conf.clear()
    return pub.decode().strip("\n")

def get_conf_listen_port(config_name, wg_conf_path):
    # ...
    conf = configparser.ConfigParser(strict=False)
    conf.read(wg_conf_path + "/" + config_name + ".conf")
    port = ""
    try:
        port = conf.get("Interface", "ListenPort")
    except:
        if get_conf_status(config_name) == "running":
            port = subprocess.check_output("wg show "+config_name+" listen-port", shell=True)
            port = port.decode("UTF-8")
    conf.clear()
    return port
def get_conf_status(config_name):
    ifconfig = dict(ifcfg.interfaces().items())
    if config_name in ifconfig.keys():
        return "running"
    else:
        return "stopped"
def get_conf_total_data(config_name):
    # ...
    db = TinyDB('db/' + config_name + '.json')
    upload_total = 0
    download_total = 0
    for i in db.all():
        upload_total += i['total_sent']
        download_total += i['total_receive']
        for k in i['traffic']:
            upload_total += k['total_sent']
            download_total += k['total_receive']
    total = round(upload_total + download_total, 4)
    upload_total = round(upload_total, 4)
    download_total = round(download_total, 4)
    db.close()
    return [total, upload_total, download_total]
def get_conf_list(wg_conf_path):
    conf = []
    for i in os.listdir(wg_conf_path):
        if regex_match("^(.{1,}).(conf)$", i):
            i = i.replace('.conf', '')
            temp = {"conf": i, "status": get_conf_status(i), "public_key": get_conf_pub_key(i,wg_conf_path)}
            if temp['status'] == "running":
                temp['checked'] = 'checked'
            else:
                temp['checked'] = ""
            conf.append(temp)
    if len(conf) > 0:
        conf = sorted(conf, key=itemgetter('conf'))
    return conf

def gen_private_key():
    # ...
    gen = subprocess.check_output('wg genkey > private_key.txt && wg pubkey < private_key.txt > public_key.txt',
                                shell=True)
    private = open('private_key.txt')
    private_key = private.readline().strip()
    public = open('public_key.txt')
    public_key = public.readline().strip()
    data = {"private_key": private_key, "public_key": public_key}
    private.close()
    public.close()
    os.remove('private_key.txt')
    os.remove('public_key.txt')
    return data
def gen_public_key(private_key):
    # ...
    pri_key_file = open('private_key.txt', 'w')
    pri_key_file.write(private_key)
    pri_key_file.close()
    try:
        check = subprocess.check_output("wg pubkey < private_key.txt > public_key.txt", shell=True)
        public = open('public_key.txt')
        public_key = public.readline().strip()
        os.remove('private_key.txt')
        os.remove('public_key.txt')
        return {"status": 'success', "msg": "", "data": public_key}
    except subprocess.CalledProcessError as exc:
        os.remove('private_key.txt')
        return {"status": 'failed', "msg": "Key is not the correct length or format", "data": ""}

def check_key_match(private_key, public_key, config_name):
    # ...
    result = gen_public_key(private_key)
    if result['status'] == 'failed':
        return result
    else:
        db = TinyDB('db/' + config_name + '.json')
        peers = Query()
        match = db.search(peers.id == result['data'])
        if len(match) != 1 or result['data'] != public_key:
            return {'status': 'failed', 'msg': 'Please check your private key, it does not match with the public key.'}
        else:
            return {'status': 'success'}
def check_repeat_allowed_IP(public_key, ip, config_name):
    # ...
    db = TinyDB('db/' + config_name + '.json')
    peers = Query()
    peer = db.search(peers.id == public_key)
    if len(peer) != 1:
        return {'status': 'failed', 'msg': 'Peer does not exist'}
    else:
        existed_ip = db.search((peers.id != public_key) & (peers.allowed_ip == ip))
        if len(existed_ip) != 0:
            return {'status': 'failed', 'msg': "Allowed IP already taken by another peer."}
        else:
            return {'status': 'success'}

def add_peer_to_conf(config_name, public_key, allowed_ips, wg_conf_path):
    # ...
    try:
        status = subprocess.check_output(
            "wg set " + config_name + " peer " + public_key + " allowed-ips " + allowed_ips, shell=True,
            stderr=subprocess.STDOUT)
        status = subprocess.check_output("wg-quick save " + config_name, shell=True, stderr=subprocess.STDOUT)
        return "true"
    except subprocess.CalledProcessError as exc:
        return exc.output.strip()

def remove_peer_from_conf(config_name, delete_key, wg_conf_path):
    # ...
    try:
        status = subprocess.check_output("wg set " + config_name + " peer " + delete_key + " remove", shell=True,
                                         stderr=subprocess.STDOUT)
        status = subprocess.check_output("wg-quick save " + config_name, shell=True, stderr=subprocess.STDOUT)
        return "true"

    except subprocess.CalledProcessError as exc:
        return exc.output.strip()
def update_peer_allowed_ips(config_name, peer_id, allowed_ip):
    try:
        if allowed_ip == "":
            allowed_ip = '""'
        change_ip = subprocess.check_output(f'wg set {config_name} peer {peer_id} allowed-ips {allowed_ip}',
                                          shell=True, stderr=subprocess.STDOUT)
        save_change_ip = subprocess.check_output(f'wg-quick save {config_name}', shell=True,
                                               stderr=subprocess.STDOUT)
        if change_ip.decode("UTF-8") != "":
            return False, change_ip.decode("UTF-8")

        return True, ""
    except subprocess.CalledProcessError as exc:
        return False, exc.output.decode("UTF-8").strip()

def switch_interface(config_name, operation):
    # ...
    if operation not in ["up", "down"]:
        raise ValueError("Invalid operation.  Must be 'up' or 'down'.")
    try:
        status = subprocess.check_output(f"wg-quick {operation} {config_name}", shell=True)
        return "success"
    except Exception:
        return "failed"

def create_client_config(config_name, data, wg_conf_path, default_dns, default_endpoint_allowed_ip, base_ip, remote_endpoint):
    # ...
    db = TinyDB(f"db/{config_name}.json")
    peers = Query()
    keys = get_conf_peer_key(config_name)
    private_key=""
    public_key=""
    check = False
    while not check:
        key = gen_private_key()
        private_key = key["private_key"]
        public_key = key["public_key"]
        if len(public_key) != 0 and public_key not in keys:
            check=True
    existing_ips = [
    int(peer['allowed_ip'].split('.')[3].split('/')[0])
    for peer in db.all()
    if 'allowed_ip' in peer and peer['allowed_ip'].startswith(base_ip)
    ]
    next_ip = max(existing_ips) + 1 if existing_ips else 2
    allowed_ips = f"{base_ip}.{next_ip}/32"
    if db.search(peers.allowed_ip == allowed_ips):
        return None, "IP already exists"
    try:
        status = subprocess.check_output(
            "wg set " + config_name + " peer " + public_key + " allowed-ips " + allowed_ips, shell=True,
            stderr=subprocess.STDOUT)
        status = subprocess.check_output("wg-quick save " + config_name, shell=True, stderr=subprocess.STDOUT)
        get_all_peers_data(config_name, wg_conf_path)
        db.update({"name": data['name'], "private_key": private_key, "DNS": default_dns,
                "endpoint_allowed_ip": default_endpoint_allowed_ip},
                peers.id == public_key)
        db.close()
    except subprocess.CalledProcessError as exc:
        db.close()
        return None,exc.output.strip()

    server_public_key = get_conf_pub_key(config_name, wg_conf_path)
    listen_port = get_conf_listen_port(config_name,wg_conf_path)
    endpoint = f"{remote_endpoint}:{listen_port}"
    filename = data["name"]
    if len(filename) == 0:
        filename = "Untitled_Peers"
    else:
        filename = data["name"]
                # Clean filename
        illegal_filename = [".", ",", "/", "?", "<", ">", "\\", ":", "*", '|' '\"', "com1", "com2", "com3",
                        "com4", "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4",
                    "lpt5", "lpt6", "lpt7", "lpt8", "lpt9", "con", "nul", "prn"]
        for i in illegal_filename:
            filename = filename.replace(i, "")
        if len(filename) == 0:
            filename = "Untitled_Peer"
        filename = "".join(filename.split(' '))
        filename = filename + "_" + config_name

    config_content = f"""# {data['name']}
            [Interface]
            PrivateKey = {private_key}
            Address = {allowed_ips}
            DNS = {default_dns}

            [Peer]
            PublicKey = {server_public_key}
            Endpoint ={endpoint}
            AllowedIPs = 0.0.0.0/0
            PersistentKeepalive = {data.get('keep_alive', 25)}
            """
    print(config_content)
    return config_content, None

def generate_peer_config(config_name, peer_id, wg_conf_path, remote_endpoint):
    db = TinyDB("db/" + config_name + ".json")
    peers = Query()
    get_peer = db.search(peers.id == peer_id)


    if len(get_peer) == 1:
        peer = get_peer[0]
        if peer['private_key'] != "":
            public_key = get_conf_pub_key(config_name, wg_conf_path)
            listen_port = get_conf_listen_port(config_name, wg_conf_path)
            endpoint = remote_endpoint + ":" + listen_port
            private_key = peer['private_key']
            allowed_ip = peer['allowed_ip']
            DNS = peer['DNS']
            endpoint_allowed_ip = peer['endpoint_allowed_ip']
            filename = peer['name']
            if len(filename) == 0:
                filename = "Untitled_Peers"
            else:
                filename = peer['name']
                # Clean filename
                illegal_filename = [".", ",", "/", "?", "<", ">", "\\", ":", "*", '|' '\"', "com1", "com2", "com3",
                                    "com4", "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4",
                                    "lpt5", "lpt6", "lpt7", "lpt8", "lpt9", "con", "nul", "prn"]
                for i in illegal_filename:
                    filename = filename.replace(i, "")
                if len(filename) == 0:
                    filename = "Untitled_Peer"
                filename = "".join(filename.split(' '))
            filename = filename + "_" + config_name
            config_content = "[Interface]\nPrivateKey = " + private_key + "\nAddress = " + allowed_ip + "\nDNS = " + DNS + "\n\n[Peer]\nPublicKey = " + public_key + "\nAllowedIPs = "+endpoint_allowed_ip+"\nEndpoint = " + endpoint
            return config_content, filename
    return None, None


# Các hàm khác liên quan đến WireGuard...