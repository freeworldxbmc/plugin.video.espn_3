import re
import os
import sys
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import json
import string, random
import urllib, urllib2
import HTMLParser

import base64

selfAddon = xbmcaddon.Addon(id='plugin.video.espn_3')
translation = selfAddon.getLocalizedString
defaultimage = 'special://home/addons/plugin.video.espn_3/icon.png'
defaultfanart = 'special://home/addons/plugin.video.espn_3/fanart.jpg'
defaultlive = 'special://home/addons/plugin.video.espn_3/resources/media/new_live.png'
defaultreplay = 'special://home/addons/plugin.video.espn_3/resources/media/new_replay.png'
defaultupcoming = 'special://home/addons/plugin.video.espn_3/resources/media/new_upcoming.png'
StreamType = selfAddon.getSetting('StreamType')
pluginpath = selfAddon.getAddonInfo('path')
pluginhandle = int(sys.argv[1])

ADDONDATA = xbmc.translatePath('special://profile/addon_data/plugin.video.espn_3/')
if not os.path.exists(ADDONDATA):
    os.makedirs(ADDONDATA)
USERFILE = os.path.join(ADDONDATA,'userdata.xml')

# KODI ADDON GLOBALS
ADDON_HANDLE = int(sys.argv[1])
ROOTDIR = xbmcaddon.Addon(id='plugin.video.espn_3').getAddonInfo('path')
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_PATH = xbmc.translatePath(ADDON.getAddonInfo('path'))
ADDON_PATH_PROFILE = xbmc.translatePath(ADDON.getAddonInfo('profile'))
if not os.path.exists(ADDON_PATH_PROFILE):
        os.makedirs(ADDON_PATH_PROFILE)
KODI_VERSION = float(re.findall(r'\d{2}\.\d{1}', xbmc.getInfoLabel("System.BuildVersion"))[0])
LOCAL_STRING = ADDON.getLocalizedString
FANART = ROOTDIR+"/fanart.jpg"
ICON = ROOTDIR+"/icon.png"

#Settings file location
settings = xbmcaddon.Addon(id='plugin.video.espn_3')

#User Agents
UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12H143'
UA_PC = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36'
UA_ADOBE_PASS = 'AdobePassNativeClient/1.9 (iPhone; U; CPU iPhone OS 8.4 like Mac OS X; en-us)'
UA_NBCSN = 'AppleCoreMedia/1.0.0.12H143 (iPhone; U; CPU OS 8_4 like Mac OS X; en_us)'
UA_ANDROID = 'AdobePassNativeClient/1.8 (Linux; U; Android 5.1.1; en-us)'

def CLEAR_SAVED_DATA():
    try:
        os.remove(ADDON_PATH_PROFILE+'/device.id')
    except:
        pass
    try:
        os.remove(ADDON_PATH_PROFILE+'/provider.info')
    except:
        pass
    try:
        os.remove(ADDON_PATH_PROFILE+'/cookies.lwp')
    except:
        pass
    try:
        os.remove(ADDON_PATH_PROFILE+'/auth.token')
    except:
        pass
    try:
        for root, dirs, files in os.walk(ADDON_PATH_PROFILE):
            for currentFile in files:
                if currentFile.lower().endswith('.xml') and not currentFile.lower() == 'settings.xml':
                    os.remove(os.path.join(ADDON_PATH_PROFILE, currentFile))
    except:
        pass
    ADDON.setSetting(id='ClearData', value='false')

if selfAddon.getSetting('ClearData') == 'true':
    CLEAR_SAVED_DATA()

#Create Random Device ID and save it to a file
fname = os.path.join(ADDON_PATH_PROFILE, 'device.id')
if not os.path.isfile(fname):
    new_device_id = ''.join([random.choice('0123456789abcdef') for x in range(16)])
    device_file = open(fname,'w')
    device_file.write(new_device_id)
    device_file.close()

fname = os.path.join(ADDON_PATH_PROFILE, 'device.id')
device_file = open(fname,'r')
DEVICE_ID = device_file.readline()
device_file.close()

#Event Colors
FREE = 'FF43CD80'
LIVE = 'FF00B7EB'
UPCOMING = 'FFFFB266'
FREE_UPCOMING = 'FFCC66FF'
