#!/usr/bin/python
#
#
# Written by Ksosez, BlueCop, Romans I XVI, locomot1f, MetalChris
# Released under GPL(v2)

import urllib, xbmcplugin, xbmcaddon, xbmcgui, os, random, string, re
import time
from adobe import ADOBE
from globals import *
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import base64

import player_config
import events
import util
from espn import ESPN
from mso_provider import get_mso_provider
from user_details import UserDetails
import urlparse

LIVE_EVENTS_MODE = 'LIVE_EVENTS'
PLAY_MODE = 'PLAY'
LIST_SPORTS_MODE = 'LIST_SPORTS'
INDEX_SPORTS_MODE = 'INDEX_SPORTS'
UPCOMING_MODE = 'UPCOMING'
NETWORK_ID = 'NETWORK_ID'
EVENT_ID = 'EVENT_ID'
SIMULCAST_AIRING_ID = 'SIMULCAST_AIRING_ID'
DESKTOP_STREAM_SOURCE = 'DESKTOP_STREAM_SOURCE'

ESPN_URL = 'ESPN_URL'
MODE = 'MODE'
SPORT = 'SPORT'

BAM_NS = '{http://services.bamnetworks.com/media/types/2.1}'

def CATEGORIES():
    include_premium = selfAddon.getSetting('ShowPremiumChannels') == 'true'
    channel_list = events.get_channel_list(include_premium)
    curdate = datetime.utcnow()
    upcoming = int(selfAddon.getSetting('upcoming'))+1
    days = (curdate+timedelta(days=upcoming)).strftime("%Y%m%d")
    addDir(translation(30029),
           dict(ESPN_URL=events.get_live_events_url(channel_list), MODE=LIVE_EVENTS_MODE),
           defaultlive)
    addDir(translation(30030),
           dict(ESPN_URL=events.get_upcoming_events_url(channel_list) + '&endDate='+days+'&startDate='+curdate.strftime("%Y%m%d"), MODE=LIST_SPORTS_MODE),
           defaultupcoming)
    enddate = '&endDate='+ (curdate+timedelta(days=1)).strftime("%Y%m%d")
    replays1 = [5,10,15,20,25]
    replays1 = replays1[int(selfAddon.getSetting('replays1'))]
    start1 = (curdate-timedelta(days=replays1)).strftime("%Y%m%d")
    replays2 = [10,20,30,40,50]
    replays2 = replays2[int(selfAddon.getSetting('replays2'))]
    start2 = (curdate-timedelta(days=replays2)).strftime("%Y%m%d")
    replays3 = [30,60,90,120]
    replays3 = replays3[int(selfAddon.getSetting('replays3'))]
    start3 = (curdate-timedelta(days=replays3)).strftime("%Y%m%d")
    replays4 = [60,90,120,240]
    replays4 = replays4[int(selfAddon.getSetting('replays4'))]
    start4 = (curdate-timedelta(days=replays4)).strftime("%Y%m%d")
    startAll = (curdate-timedelta(days=365)).strftime("%Y%m%d")
    addDir(translation(30031)+str(replays1)+' Days',
           dict(ESPN_URL=events.get_replay_events_url(channel_list) +enddate+'&startDate='+start1, MODE=LIST_SPORTS_MODE),
           defaultreplay)
    addDir(translation(30031)+str(replays2)+' Days',
           dict(ESPN_URL=events.get_replay_events_url(channel_list) +enddate+'&startDate='+start2, MODE=LIST_SPORTS_MODE),
           defaultreplay)
    addDir(translation(30031)+str(replays3)+' Days',
           dict(ESPN_URL=events.get_replay_events_url(channel_list) +enddate+'&startDate='+start3, MODE=LIST_SPORTS_MODE),
           defaultreplay)
    addDir(translation(30031)+str(replays3)+'-'+str(replays4)+' Days',
           dict(ESPN_URL=events.get_replay_events_url(channel_list) +'&endDate='+start3+'&startDate='+start4, MODE=LIST_SPORTS_MODE),
           defaultreplay)
    addDir(translation(30032),
           dict(ESPN_URL=events.get_replay_events_url(channel_list) +enddate+'&startDate='+startAll, MODE=LIST_SPORTS_MODE),
           defaultreplay)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def LISTNETWORKS(url,name):
    pass

def LISTSPORTS(args):
    espn_url = args.get(ESPN_URL)[0]
    if 'action=replay' in espn_url:
        image = defaultreplay
    elif 'action=upcoming' in espn_url:
        image = defaultupcoming
    else:
        image = defaultimage
    addDir(translation(30034), dict(ESPN_URL=espn_url, MODE=LIVE_EVENTS_MODE), image)
    sports = []
    sport_elements = events.get_soup_events_cached(espn_url).findall('.//sportDisplayValue')
    for sport in sport_elements:
        sport = sport.text.encode('utf-8')
        if sport not in sports:
            sports.append(sport)
    for sport in sports:
        addDir(sport, dict(ESPN_URL=espn_url, MODE=INDEX_SPORTS_MODE, SPORT=sport), image)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def INDEX_EVENT(event, live, upcoming, replay, chosen_sport):
    sport = event.find('sportDisplayValue').text.encode('utf-8')
    desktopStreamSource = event.find('desktopStreamSource').text
    ename = event.find('name').text
    eventid = event.get('id')
    simulcastAiringId = event.find('simulcastAiringId').text
    networkid = event.find('networkId').text
    if networkid is not None:
        network = player_config.get_network_name(networkid)
    sport2 = event.find('sport').text
    if sport <> sport2:
        sport += ' ('+sport2+')'
    league = event.find('league').text
    location = event.find('site').text
    fanart = event.find('.//thumbnail/large').text
    fanart = fanart.split('&')[0]
    mpaa = event.find('parentalRating').text
    starttime = int(event.find('startTimeGmtMs').text)/1000
    etime = time.strftime("%I:%M %p",time.localtime(float(starttime)))
    endtime = int(event.find('endTimeGmtMs').text)/1000
    start = time.strftime("%m/%d/%Y %I:%M %p",time.localtime(starttime))
    aired = time.strftime("%Y-%m-%d",time.localtime(starttime))
    udate = time.strftime("%m/%d",time.localtime(starttime))
    now = datetime.now().strftime('%H%M')
    etime24 = time.strftime("%H%M",time.localtime(starttime))
    aspect_ratio = event.find('aspectRatio').text
    length = str(int(round((endtime - time.time()))))
    title_time = etime
    if live and now > etime24:
        color = str(selfAddon.getSetting('color'))
    elif live:
        color = '999999'
    else:
        color = 'E0E0E0'
        length = str(int(round((endtime - starttime))))
        title_time = ' - '.join((udate, etime))

    if network == 'longhorn':
        channel_color = 'BF5700'
    elif network == 'sec' or network == 'secplus':
        channel_color = '004C8D'
    else:
        channel_color = 'CC0000'

    ename = '[COLOR=FF%s]%s[/COLOR] [COLOR=FFB700EB]%s[/COLOR] [COLOR=FF%s]%s[/COLOR]' % (channel_color, network, title_time, color, ename)

    length_minutes = int(length) / 60

    end = event.find('summary').text
    if end is None or len(end) == 0:
        end = event.find('caption').text

    if end is None:
        end = ''
    end += '\nNetwork: ' + network

    plot = ''
    if sport <> None and sport <> ' ':
        plot += 'Sport: '+sport+'\n'
    if league <> None and league <> ' ':
        plot += 'League: '+league+'\n'
    if location <> None and location <> ' ':
        plot += 'Location: '+location+'\n'
    if start <> None and start <> ' ':
        plot += 'Air Date: '+start+'\n'
    if length <> None and length <> ' ' and live:
        plot += 'Duration: Approximately '+ str(length_minutes)+' minutes remaining'+'\n'
    elif length <> None and length <> ' ' and (replay or upcoming):
        plot += 'Duration: '+ str(length_minutes) +' minutes'+'\n'
    plot += end
    infoLabels = {'title': ename,
                  'genre':sport,
                  'plot':plot,
                  'aired':aired,
                  'premiered':aired,
                  'duration':length,
                  'studio':network,
                  'mpaa':mpaa,
                  'videoaspect' : aspect_ratio}

    authurl = dict()
    authurl[EVENT_ID] = eventid
    authurl[SIMULCAST_AIRING_ID] = simulcastAiringId
    authurl[DESKTOP_STREAM_SOURCE] = desktopStreamSource
    authurl[NETWORK_ID] = networkid
    authurl[MODE] = UPCOMING_MODE if upcoming else PLAY_MODE
    addLink(ename, authurl, fanart, fanart, infoLabels=infoLabels)

def INDEX(args):
    espn_url = args.get(ESPN_URL)[0]
    chosen_sport = args.get(SPORT, None)
    if chosen_sport is not None:
        chosen_sport = chosen_sport[0]
    chosen_network = args.get(NETWORK_ID, None)
    if chosen_network is not None:
        chosen_network = chosen_network[0]
    else:
        include_premium = selfAddon.getSetting('ShowPremiumChannels') == 'true'
        if not include_premium:
            chosen_network = 'n360'
    live = 'action=live' in espn_url
    upcoming = 'action=upcoming' in espn_url
    replay = 'action=replay' in espn_url
    if live:
        data = events.get_events(espn_url)
    else:
        data = events.get_soup_events_cached(espn_url).findall(".//event")
    num_espn3 = 0;
    for event in data:
        sport = event.find('sportDisplayValue').text.encode('utf-8')
        if chosen_sport <> sport and chosen_sport is not None:
            continue
        networkid = event.find('networkId').text
        if chosen_network <> networkid and chosen_network is not None:
            continue
        if networkid == 'n360' and chosen_network is None :
            num_espn3 = num_espn3 + 1
        else:
            INDEX_EVENT(event, live, upcoming, replay, chosen_sport)
    # Dir for ESPN3
    if chosen_network is None:
        translation_number = 30191 if num_espn3 == 1 else 30190
        addDir('[COLOR=FFCC0000]' + (translation(translation_number) % num_espn3) + '[/COLOR]',
           dict(ESPN_URL=espn_url, MODE=LIVE_EVENTS_MODE, NETWORK_ID='n360'),
           defaultlive)
    xbmcplugin.setContent(pluginhandle, 'episodes')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def PLAYESPN3(url):
    PLAY(url,'n360')

def check_blackout(authurl):
    tree = util.get_url_as_xml_soup(authurl)
    authstatus = tree.find('.//' + BAM_NS + 'auth-status')
    blackoutstatus = tree.find('.//' + BAM_NS + 'blackout-status')
    if blackoutstatus.find('.//' + BAM_NS + 'errorCode') is not None:
        if blackoutstatus.find('.//' + BAM_NS + 'errorMessage') is not None:
            dialog = xbmcgui.Dialog()
            dialog.ok(translation(30040), blackoutstatus.find('.//' + BAM_NS + 'errorMessage').text)
            return (tree, True)
    if authstatus.find('.//' + BAM_NS + 'errorCode') is not None or authstatus.find('.//' + BAM_NS + 'errorMessage') is not None:
        dialog = xbmcgui.Dialog()
        import textwrap
        errormessage = '%s - %s' % (authstatus.find('.//' + BAM_NS + 'errorCode').text,  authstatus.find('.//' + BAM_NS + 'errorMessage').text)
        try:
            errormessage = textwrap.fill(errormessage, width=50).split('\n')
            dialog.ok(translation(30037), errormessage[0],errormessage[1],errormessage[2])
        except:
            dialog.ok(translation(30037), errormessage[0])
        return (tree, True)
    return (tree, False)

def PLAY_PROTECTED_CONTENT(args):

    if not check_user_settings():
        return

    user_data = player_config.get_user_data()
    affiliateid = user_data['name']

    simulcastAiringId = args.get(SIMULCAST_AIRING_ID)[0]
    streamType = args.get(DESKTOP_STREAM_SOURCE)[0]
    networkId = args.get(NETWORK_ID)[0]
    eventId = args.get(EVENT_ID)[0]

    requestor = ESPN()
    mso_provider = get_mso_provider(selfAddon.getSetting('provider'))
    user_details = UserDetails(selfAddon.getSetting('username'), selfAddon.getSetting('password'))


    adobe = ADOBE(requestor, mso_provider, user_details)
    media_token = adobe.GET_MEDIA_TOKEN()
    resource_id = requestor.get_resource_id()

    if media_token is None:
        return

    start_session_url = player_config.get_start_session_url()
    start_session_url += '&affiliate='+affiliateid
    start_session_url += '&channel='+player_config.get_network_name(networkId)
    start_session_url += '&partner=watchespn'
    start_session_url += '&playbackScenario=FMS_CLOUD'
    start_session_url += '&token='+urllib.quote(base64.b64encode(media_token))
    start_session_url += '&resource=' + urllib.quote(base64.b64encode(resource_id))
    start_session_url += '&simulcastAiringId='+simulcastAiringId
    start_session_url += '&tokenType=ADOBEPASS'
    start_session_url += '&eventId=' + eventId
    start_session_url += '&cdnName=PRIMARY_AKAMAI'
    start_session_url += '&playerId=domestic'

    xbmc.log('ESPN3: start_session_url: ' + start_session_url)

    (tree, result) = check_blackout(start_session_url)
    if result:
        return


    pkan = tree.find('.//' + BAM_NS + 'pkanJar').text
    if streamType == 'HDS':
        # FFMPEG does not support hds so use hls
        smilurl = tree.find('.//' + BAM_NS + 'hls-backup-url').text
    else: # HLS
        smilurl = tree.find('.//' + BAM_NS + 'url').text
    xbmc.log('ESPN3:  smilurl: '+smilurl)
    xbmc.log('ESPN3:  streamType: '+streamType)
    if smilurl == ' ' or smilurl == '':
        dialog = xbmcgui.Dialog()
        dialog.ok(translation(30037), translation(30038),translation(30039))
        return

    finalurl = smilurl
    #ua = urllib.quote('VisualOn OSMP+ Player(Linux;Android;WatchESPN/1.0_Handset)')
    ua = UA_PC
    finalurl = finalurl + '|Connection=keep-alive&User-Agent=' + ua + '&Cookie=_mediaAuth=' + urllib.quote(base64.b64encode(pkan))
    xbmc.log('ESPN3: finalurl %s' % finalurl)
    item = xbmcgui.ListItem(path=finalurl)
    return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

def PLAY_FREE_CONTENT(args):
    free_content_check = player_config.can_access_free_content()
    if not free_content_check:
        xbmc.log('ESPN3: User needs login to ESPN3')
        return PLAY_PROTECTED_CONTENT(args)
        #dialog = xbmcgui.Dialog()
        #dialog.ok(translation(30037), translation(30140),translation(30150))

    user_data = player_config.get_user_data()
    affiliateid = user_data['name']

    eventid = args.get(EVENT_ID)[0]
    simulcastAiringId = args.get(SIMULCAST_AIRING_ID)[0]
    streamType = args.get(DESKTOP_STREAM_SOURCE)[0]
    networkId = args.get(NETWORK_ID)[0]

    pk = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(51)])
    pkan = pk + ('%3D')
    network = player_config.get_network(networkId)
    playedId = network.get('playerId')
    cdnName = network.get('defaultCdn')
    channel = network.get('name')

    authurl = player_config.get_start_session_url()
    authurl += '&affiliate='+affiliateid
    authurl += '&pkan='+pkan
    authurl += '&pkanType=SWID'
    authurl += '&simulcastAiringId='+simulcastAiringId
    authurl += '&cdnName='+cdnName
    authurl += '&channel='+channel
    authurl += '&playbackScenario=FMS_CLOUD'
    authurl += '&eventid='+eventid
    authurl += '&rand='+str(random.randint(100000,999999))
    authurl += '&playerId='+playedId

    xbmc.log('ESPN3: Content URL %s' % authurl)

    (tree, result) = check_blackout(authurl)
    if result:
        return

    if streamType == 'HDS':
        # FFMPEG does not support hds so use hls
        smilurl = tree.find('.//' + BAM_NS + 'hls-backup-url').text
    else: # HLS
        smilurl = tree.find('.//' + BAM_NS + 'url').text
    xbmc.log('ESPN3:  smilurl: %s' % smilurl)
    if smilurl is None:
        smilurl = tree.find('.//' + BAM_NS + 'hls-backup-url').text
        xbmc.log('ESPN3:  smilurl hls backup: %s' % smilurl)
    if smilurl is None or smilurl == ' ' or smilurl == '':
        dialog = xbmcgui.Dialog()
        dialog.ok(translation(30037), translation(30038),translation(30039))
        return

    finalurl = smilurl
    item = xbmcgui.ListItem(path=finalurl)
    return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

def check_user_settings():
    mso_provider = get_mso_provider(selfAddon.getSetting('provider'))
    username = selfAddon.getSetting('username')
    password = selfAddon.getSetting('password')
    if mso_provider is None:
        dialog = xbmcgui.Dialog()
        dialog.ok(translation(30037), translation(30100))
        return False
    if username is None:
        dialog = xbmcgui.Dialog()
        dialog.ok(translation(30037), translation(30110))
        return False
    if password is None:
        dialog = xbmcgui.Dialog()
        dialog.ok(translation(30037), translation(30120))
        return False
    return True


def PLAY(args):
    networkId = args.get(NETWORK_ID)[0]
    if networkId == 'n360':
        PLAY_FREE_CONTENT(args)
    else:
        PLAY_PROTECTED_CONTENT(args)

def addLink(name, url, iconimage, fanart=False, infoLabels=False):
    u = sys.argv[0] + '?' + urllib.urlencode(url)
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)

    if not infoLabels:
        infoLabels={"Title": name}
    liz.setInfo(type="Video", infoLabels=infoLabels)
    liz.setProperty('IsPlayable', 'true')
    liz.setIconImage(iconimage)
    if not fanart:
        fanart=defaultfanart
    liz.setProperty('fanart_image',fanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, iconimage, fanart=False, infoLabels=False):
    u = sys.argv[0] + '?' + urllib.urlencode(url)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    if not infoLabels:
        infoLabels={"Title": name}
    liz.setInfo(type="Video", infoLabels=infoLabels)
    if not fanart:
        fanart=defaultfanart
    liz.setProperty('fanart_image',fanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get(MODE, None)

xbmc.log('ESPN3: args %s' % args)

if mode == None:
    xbmc.log("Generate Main Menu")
    CATEGORIES()
elif mode[0] == LIVE_EVENTS_MODE:
    xbmc.log("Indexing Videos")
    INDEX(args)
elif mode[0] == LIST_SPORTS_MODE:
    xbmc.log("List sports")
    LISTSPORTS(args)
elif mode[0] == INDEX_SPORTS_MODE:
    xbmc.log("Index by sport")
    INDEX(args)
elif mode[0] == PLAY_MODE:
    PLAY(args)
elif mode[0] == UPCOMING_MODE:
    xbmc.log("Upcoming")
    dialog = xbmcgui.Dialog()
    dialog.ok(translation(30035), translation(30036))


