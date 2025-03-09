# models/dashboard_model.py
# (tiếp tục từ phần trước)

from tinydb import TinyDB, Query
import re
from operator import itemgetter
from models.wireguard_model import get_all_peers_data

def get_peers(config_name, search, sort_t):
    get_all_peers_data(config_name)
    db = TinyDB('db/' + config_name + '.json')
    peer = Query()
    if not search:
        result = db.all()
    else:
        result = db.search(peer.name.matches(f'(.*){re.escape(search)}(.*)'))  # Sử dụng f-string

    if sort_t in ['name', 'status', 'allowed_ip']: # Thêm kiểm tra hợp lệ
        result = sorted(result, key=itemgetter(sort_t))  # Dùng itemgetter
    # Không cần else, vì nếu sort_t không hợp lệ, ta không sắp xếp
    db.close()
    return result


def get_peer_data(config_name, peer_id):
    db = TinyDB("db/" + config_name + ".json")
    peers = Query()
    result = db.search(peers.id == peer_id)
    db.close()

    if not result:  # Kiểm tra trường hợp không tìm thấy
        return None

    data = {
        "name": result[0]['name'],
        "allowed_ip": result[0]['allowed_ip'],
        "DNS": result[0]['DNS'],
        "private_key": result[0]['private_key'],
        "endpoint_allowed_ip": result[0]['endpoint_allowed_ip'],
        "mtu": result[0]['mtu'],
        "keep_alive": result[0]['keepalive']
    }
    return data

def update_peer_data(config_name, peer_id, data):
    db = TinyDB("db/" + config_name + ".json")
    peers = Query()
    if db.search(peers.id == peer_id):
        db.update(
            {"name": data['name'], "private_key": data['private_key'],
            "DNS": data['DNS'], "endpoint_allowed_ip": data['endpoint_allowed_ip'],
            "mtu": data['mtu'],
            "keepalive": data['keep_alive']},
            peers.id == peer_id)
        db.close()
        return True # Thành công
    else:
        db.close()
        return False # Không tìm thấy peer

def add_peer(config_name, peer_data):
    db = TinyDB("db/" + config_name + ".json")
    peers = Query()
    # ... (Kiểm tra và thêm peer) ...
    public_key = peer_data['public_key']
    allowed_ips = peer_data['allowed_ips']
    endpoint_allowed_ip = peer_data['endpoint_allowed_ip']
    DNS = peer_data['DNS']
    if len(public_key) == 0 or len(DNS) == 0 or len(allowed_ips) == 0 or len(endpoint_allowed_ip) == 0:
        return False, "Please fill in all required box." # Thêm return False
    # ... (các kiểm tra khác) ...
    db.update({"name": peer_data['name'], "private_key": peer_data['private_key'], "DNS": peer_data['DNS'],
                "endpoint_allowed_ip": endpoint_allowed_ip},
                peers.id == public_key)
    db.close()
    return True, "" # Thêm return True


def remove_peer(config_name, peer_id):
    db = TinyDB("db/" + config_name + ".json")
    peers = Query()
    # ... (Xóa peer) ...
    db.remove(peers.id == peer_id)
    db.close()

# Các hàm khác liên quan đến dashboard...