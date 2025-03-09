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
        result = db.search(peer.name.matches(f'(.*){re.escape(search)}(.*)')) 

    if sort_t in ['name', 'status', 'allowed_ip']:
        result = sorted(result, key=itemgetter(sort_t))  
    db.close()
    return result


def get_peer_data(config_name, peer_id):
    db = TinyDB("db/" + config_name + ".json")
    peers = Query()
    result = db.search(peers.id == peer_id)
    db.close()

    if not result:  
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
        return True 
    else:
        db.close()
        return False 

def add_peer(config_name, peer_data):
    db = TinyDB("db/" + config_name + ".json")
    peers = Query()

    public_key = peer_data['public_key']
    allowed_ips = peer_data['allowed_ips']
    endpoint_allowed_ip = peer_data['endpoint_allowed_ip']
    DNS = peer_data['DNS']
    if len(public_key) == 0 or len(DNS) == 0 or len(allowed_ips) == 0 or len(endpoint_allowed_ip) == 0:
        return False, "Please fill in all required box."

    db.update({"name": peer_data['name'], "private_key": peer_data['private_key'], "DNS": peer_data['DNS'],
                "endpoint_allowed_ip": endpoint_allowed_ip},
                peers.id == public_key)
    db.close()
    return True, "" 


def remove_peer(config_name, peer_id):
    db = TinyDB("db/" + config_name + ".json")
    peers = Query()

    db.remove(peers.id == peer_id)
    db.close()

