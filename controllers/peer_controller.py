# Tạo controller cho peer
# controllers/peer_controller.py
from flask import render_template, request, redirect, url_for, session, jsonify
from models.wireguard_model import get_conf_list, get_conf_status, get_conf_total_data, switch_interface, get_conf_peer_key
from models.dashboard_model import get_peers, get_peer_data, update_peer_data, add_peer, remove_peer
from config import get_dashboard_conf
import urllib.parse
from models import  regex_match, check_IP_with_range, check_DNS, check_Allowed_IPs, check_remote_endpoint
from models.wireguard_model import check_key_match, check_repeat_allowed_IP, gen_private_key, gen_public_key
from icmplib import ping, multiping, traceroute, resolve, Host, Hop # Import icmplib
def get_ping_ip_controller():
    # ...
    config_name = request.form['config']  # Sửa thành config_name cho đúng
    db = TinyDB('db/' + config_name + '.json')
    html = ""
    for i in db.all():
        html += '<optgroup label="' + i['name'] + ' - ' + i['id'] + '">'
        allowed_ip = str(i['allowed_ip']).split(",")
        for k in allowed_ip:
            k = k.split("/")
            if len(k) == 2:
                html += "<option value=" + k[0] + ">" + k[0] + "</option>"
        endpoint = str(i['endpoint']).split(":")
        if len(endpoint) == 2:
            html += "<option value=" + endpoint[0] + ">" + endpoint[0] + "</option>"
        html += "</optgroup>"
    return html

def ping_ip_controller():
    # ...
    try:
        result = ping('' + request.form['ip'] + '', count=int(request.form['count']), privileged=True, source=None)
        returnjson = {
            "address": result.address,
            "is_alive": result.is_alive,
            "min_rtt": result.min_rtt,
            "avg_rtt": result.avg_rtt,
            "max_rtt": result.max_rtt,
            "package_sent": result.packets_sent,
            "package_received": result.packets_received,
            "package_loss": result.packet_loss
        }
        if returnjson['package_loss'] == 1.0:
            returnjson['package_loss'] = returnjson['package_sent']


        return jsonify(returnjson)
    except Exception:
        return "Error"
def traceroute_ip_controller():
    # ...
    try:
        result = traceroute('' + request.form['ip'] + '', first_hop=1, max_hops=30, count=1, fast=True)
        returnjson = []
        last_distance = 0
        for hop in result:
            if last_distance + 1 != hop.distance:
                returnjson.append({"hop": "*", "ip": "*", "avg_rtt": "", "min_rtt": "", "max_rtt": ""})
            returnjson.append({"hop": hop.distance, "ip": hop.address, "avg_rtt": hop.avg_rtt, "min_rtt": hop.min_rtt,
                            "max_rtt": hop.max_rtt})
            last_distance = hop.distance
        return jsonify(returnjson)
    except Exception:
        return "Error"