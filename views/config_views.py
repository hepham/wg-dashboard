from flask import Blueprint
from controllers.dashboard_controller import  add_peer_controller, remove_peer_controller, save_peer_setting, get_peer_data_controller, generate_peer, generate_public_key, check_key_match_controller, download, create_client

config_views = Blueprint('config_views', __name__)


@config_views.route('/add_peer/<config_name>', methods=['POST'])
def add_peer_route(config_name):
    return add_peer_controller(config_name)


@config_views.route('/remove_peer/<config_name>', methods=['POST'])
def remove_peer_route(config_name):
    return remove_peer_controller(config_name)


@config_views.route('/save_peer_setting/<config_name>', methods=['POST'])
def save_peer_setting_route(config_name):
    return save_peer_setting(config_name)


@config_views.route('/get_peer_data/<config_name>', methods=['POST'])
def get_peer_data_route(config_name):
    return get_peer_data_controller(config_name)


@config_views.route('/generate_peer', methods=['GET'])  # Giữ nguyên route
def generate_peer_route():
    return generate_peer()


@config_views.route('/generate_public_key', methods=['POST'])  # Giữ nguyên route
def generate_public_key_route():
    return generate_public_key()


@config_views.route('/check_key_match/<config_name>', methods=['POST'])  # Giữ nguyên route
def check_key_match_route(config_name):
    return check_key_match_controller(config_name)

@config_views.route('/download/<config_name>', methods=['GET'])  # Giữ nguyên route
def download_route(config_name):
    return download(config_name)

@config_views.route('/create_client/<config_name>', methods=['POST'])
def create_client_route(config_name):
    return create_client(config_name)