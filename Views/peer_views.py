# views/peer_views.py
from flask import Blueprint
from controllers.peer_controller import  get_ping_ip_controller, ping_ip_controller, traceroute_ip_controller

peer_views = Blueprint('peer_views', __name__)


@peer_views.route('/get_ping_ip', methods=['POST'])
def get_ping_ip_route():
    return get_ping_ip_controller()

@peer_views.route('/ping_ip', methods=['POST'])
def ping_ip_route():
    return ping_ip_controller()

@peer_views.route('/traceroute_ip', methods=['POST'])
def traceroute_ip_route():
    return traceroute_ip_controller()