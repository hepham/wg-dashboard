# config.py
import configparser
import secrets
import ifcfg
import os
DASHBOARD_VERSION = 'v2.3.1'
DASHBOARD_CONF = 'wg-dashboard.ini'
DEFAULT_DNS = "1.1.1.1"
DEFAULT_ENDPOINT_ALLOWED_IP = "0.0.0.0/0"
BASE_IP = "10.66.66"

def get_dashboard_conf():
    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    return config

def set_dashboard_conf(config):
    with open(DASHBOARD_CONF, "w") as configfile:
        config.write(configfile)

def init_dashboard_config():
    config = configparser.ConfigParser(strict=False)
    if not os.path.isfile(DASHBOARD_CONF):
       conf_file = open(DASHBOARD_CONF, "w+")
    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    if "Account" not in config:
        config['Account'] = {}
    if "username" not in config['Account']:
        config['Account']['username'] = 'admin'
    if "password" not in config['Account']:
        config['Account']['password'] = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'
    if "Server" not in config:
        config['Server'] = {}
    if 'wg_conf_path' not in config['Server']:
        config['Server']['wg_conf_path'] = '/etc/wireguard'
    if 'app_ip' not in config['Server']:
        config['Server']['app_ip'] = '0.0.0.0'
    if 'app_port' not in config['Server']:
        config['Server']['app_port'] = '10086'
    if 'auth_req' not in config['Server']:
        config['Server']['auth_req'] = 'true'
    if 'version' not in config['Server'] or config['Server']['version'] != DASHBOARD_VERSION:
        config['Server']['version'] = DASHBOARD_VERSION
    if 'dashboard_refresh_interval' not in config['Server']:
        config['Server']['dashboard_refresh_interval'] = '60000'
    if 'dashboard_sort' not in config['Server']:
        config['Server']['dashboard_sort'] = 'status'
    if "Peers" not in config:
        config['Peers'] = {}
    if 'peer_global_DNS' not in config['Peers']:
        config['Peers']['peer_global_DNS'] = '1.1.1.1'
    if 'peer_endpoint_allowed_ip' not in config['Peers']:
        config['Peers']['peer_endpoint_allowed_ip'] = '0.0.0.0/0'
    if 'peer_display_mode' not in config['Peers']:
        config['Peers']['peer_display_mode'] = 'grid'
    if 'remote_endpoint' not in config['Peers']:
        config['Peers']['remote_endpoint'] = ifcfg.default_interface()['inet']
    if 'peer_MTU' not in config['Peers']:
        config['Peers']['peer_MTU'] = "1420"
    if 'peer_keep_alive' not in config['Peers']:
        config['Peers']['peer_keep_alive'] = "21"
    config.write(open(DASHBOARD_CONF, "w"))
    config.clear()