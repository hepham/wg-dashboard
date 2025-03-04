from flask import Blueprint
from controllers.dashboard_controller import index, configuration, get_config, switch
from controllers.peer_controller import get_ping_ip_controller, ping_ip_controller, traceroute_ip_controller
dashboard_views = Blueprint('dashboard_views', __name__)

@dashboard_views.route('/', methods=['GET'])
def index_route():
    return index()
@dashboard_views.route('/configuration/<config_name>', methods=['GET'])
def configuration_route(config_name):
    return configuration(config_name)

@dashboard_views.route('/get_config/<config_name>', methods=['GET'])
def get_config_route(config_name):
    return get_config(config_name)

@dashboard_views.route('/switch/<config_name>', methods=['GET'])
def switch_route(config_name):
    return switch(config_name)