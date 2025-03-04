from flask import Blueprint
from controllers.settings_controller import settings, update_account, update_peer_default, update_password, update_app_ip_port, update_wg_conf_path, update_dashboard_sort, update_dashboard_refresh_interval, switch_display_mode
settings_views = Blueprint('settings_views', __name__)

@settings_views.route('/settings', methods=['GET'])
def settings_route():
    return settings()

@settings_views.route('/update_acct', methods=['POST'])
def update_acct_route():
    return update_account()

@settings_views.route('/update_peer_default_config', methods=['POST'])
def update_peer_default_route():
    return update_peer_default()

@settings_views.route('/update_pwd', methods=['POST'])
def update_pwd_route():
    return update_password()

@settings_views.route('/update_app_ip_port', methods=['POST'])
def update_app_ip_port_route():
    return update_app_ip_port()

@settings_views.route('/update_wg_conf_path', methods=['POST'])
def update_wg_conf_path_route():
    return update_wg_conf_path()

@settings_views.route('/update_dashboard_sort', methods=['POST'])
def update_dashboard_sort_route():
    return update_dashboard_sort()


@settings_views.route('/update_dashboard_refresh_interval', methods=['POST'])
def update_dashboard_refresh_interval_route():
    return update_dashboard_refresh_interval()
@settings_views.route('/switch_display_mode/<mode>', methods=['GET'])
def switch_display_mode_route(mode):
    return switch_display_mode(mode)