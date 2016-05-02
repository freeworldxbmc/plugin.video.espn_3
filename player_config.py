#!/usr/bin/python2

import os
import time
import globals
import urllib
import xbmc
from bs4 import BeautifulSoup

import util

TIME_DIFFERENCE = 60 * 60 * 24;

PLAYER_CONFIG_FILE = 'player_config.xml'
PLAYER_CONFIG_FILE = os.path.join(globals.ADDON_PATH_PROFILE, PLAYER_CONFIG_FILE)
PLAYER_CONFIG_URL = 'https://espn.go.com/watchespn/player/config'

USER_DATA_FILE = 'user_data.xml'
USER_DATA_FILE = os.path.join(globals.ADDON_PATH_PROFILE, USER_DATA_FILE)
USER_DATA_URL = 'http://broadband.espn.go.com/espn3/auth/watchespn/userData?format=xml'

#TODO: Hook up check rights?
CHECK_RIGHTS_URL = 'http://broadband.espn.go.com/espn3/auth/espnnetworks/user'

def get_config_soup():
    return util.get_url_as_xml_soup_cache(PLAYER_CONFIG_URL, PLAYER_CONFIG_FILE, TIME_DIFFERENCE)

def get_user_data():
    return util.get_url_as_xml_soup_cache(USER_DATA_URL, USER_DATA_FILE, TIME_DIFFERENCE)

def get_networks():
    networks = get_config_soup().findall('.//network')
    return networks

def get_live_event_url():
    return get_config_soup().find('.//feed[@id=\'liveEvent\']').text

def get_replay_event_url():
    return get_config_soup().find('.//feed[@id=\'replayEvent\']').text

def get_upcoming_event_url():
    return get_config_soup().find('.//feed[@id=\'upcomingEvent\']').text

def get_start_session_url():
    return get_config_soup().find('.//feed[@id=\'startSession\']').text

def get_providers_url():
    return get_config_soup().find('.//feed[@id=\'adobePassProviders\']').text

def get_network_name(network_id):
    network = get_network(network_id)
    if network is None:
        return 'Unknown network %s' % network_id
    else:
        return network.get('name')

def get_network(network_id):
    networks = get_networks()
    for network in networks:
        if network.get('id') == network_id:
            return network
    return None

if __name__ == '__main__':
    networks = get_networks()
    for network in networks:
        print '%s - %s' % (network['id'], network['name'])

    print 'live url %s: ' % get_live_event_url()

