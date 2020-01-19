#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import re
import time

from mopidy import httpclient

import requests


logger = logging.getLogger(__name__)


class Station(object):
    id = None
    continent = None
    country = None
    city = None
    genres = None
    name = None
    stream_url = None
    image = None
    description = None
    playable = False


class RadioNetClient(object):

    base_url = 'https://radio.net/'
    api_base_url = 'https://api.radio.net/info/v2/'

    session = requests.Session()
    api_key = None
    user_login = None
    min_bitrate = 96
    max_top_stations = 100
    station_bookmarks = None

    fav_stations = []
    top_stations = []
    local_stations = []
    search_results = []

    username = None
    password = None

    def __init__(self, proxy_config=None, user_agent=None):
        super(RadioNetClient, self).__init__()
        self.session = requests.Session()
        if proxy_config is not None:
            proxy = httpclient.format_proxy(proxy_config)
            self.session.proxies.update({'http': proxy, 'https': proxy})

        full_user_agent = httpclient.format_user_agent(user_agent)
        self.session.headers.update({'user-agent': full_user_agent})
        self.session.headers.update({'cache-control': 'no-cache'})

    def set_lang(self, lang):
        langs = ['net', 'de', 'at', 'fr', 'pt', 'es', 'dk', 'se', 'it', 'pl']
        if lang in langs:
            self.base_url = self.base_url.replace(".net", "." + lang)
            self.api_base_url = self.api_base_url.replace(".net", "." + lang)
        else:
            logging.error("Radio.net not supported language: " - str(lang))

    def flush(self):
        self.fav_stations = []
        self.top_stations = []
        self.local_stations = []
        self.search_results = []

    def current_milli_time(self):
        return int(round(time.time() * 1000))

    def get_api_key(self):
        if self.api_key is not None:
            return

        try:
            tmp_str = self.session.get(self.base_url)
            m = re.search('apiKey ?= ?[\'|"](.*)[\'|"];', tmp_str.content.decode())
            self.api_key = m.group(1)
            logger.info('Radio.net: APIKEY %s' % self.api_key)
        except Exception:
            logger.error('Radio.net: Failed to connect %s retrying'
                         ' on next browse.' % self.base_url)

    def do_post(self, api_sufix, url_params=None, payload=None):
        self.get_api_key()

        if 'apikey' in url_params.keys():
            url_params['apikey'] = self.api_key

        response = self.session.post(self.api_base_url + api_sufix,
                                     params=url_params, data=payload)
        return response

    def do_get(self, api_sufix, url_params=None):
        self.get_api_key()

        if 'apikey' in url_params.keys():
            url_params['apikey'] = self.api_key

        response = self.session.get(self.api_base_url + api_sufix,
                                     params=url_params)
        return response

    def check_auth(self):
        url_params = {
            'apikey': self.api_key,
            '_': self.current_milli_time(),
        }
        logger.debug('Radio.net: Check auth.')
        api_sufix = 'user/account'

        response = self.do_post(api_sufix, url_params)

        json = response.json()
        self.user_login = json['login']
        if len(self.user_login) == 0:
            self.auth = False
        else:
            self.auth = True

    def login(self, username, password):
        self.check_auth()

        if self.auth:
            return

        self.username = username
        self.password = password

        url_params = {
            'apikey': self.api_key,
            '_': self.current_milli_time(),
        }

        logger.debug('Radio.net: Login.')
        api_sufix = 'user/login'
        payload = {
            'login': username,
            'password': password,
        }
        response = self.do_post(api_sufix, url_params, payload)

        if response.status_code is not 200:
            logger.error('Radio.net: Login error. ' + response.text)
        else:
            json = response.json()
            self.user_login = json['login']

        if self.user_login == username:
            logger.debug('Radio.net: Login successful.')

    def logout(self):
        url_params = {
            'apikey': self.api_key,
            '_': self.current_milli_time(),
        }
        api_sufix = 'user/logout'
        response = self.do_post(api_sufix, url_params)

        if response.status_code is not 200:
            logger.error('Radio.net: Error logout.')
        else:
            json = response.json()
            if len(json['login']) > 0:
                logger.error('Radio.net: Error logout.')
            else:
                logger.info('Radio.net: Logout successful.')

        self.session.close()

    def get_bookmarks(self):
        self.station_bookmarks = None

        url_params = {
            'apikey': self.api_key,
            '_': self.current_milli_time(),
            'list': 'STATION',
        }
        api_sufix = 'user/bookmarks'

        response = self.do_post(api_sufix, url_params)

        if response.status_code is not 200:
            logger.error('Radio.net: ' + response.text)
        else:
            logger.debug('Radio.net: Done get bookmarks')
            json = response.json()
            self.station_bookmarks = json['stationBookmarks']

    def __get_stream_url(self, stream_json, bitrate):
        stream_url = None

        for stream in stream_json:
            if int(stream['bitRate']) >= bitrate and \
               stream['streamStatus'] == 'VALID':
                stream_url = stream['streamUrl']
                break

        if stream_url is None and len(stream_json) > 0:
            stream_url = stream_json[0]['streamUrl']

        return stream_url

    def get_my_stations_streams(self):
        self.fav_stations = []
        for station_item in self.station_bookmarks['pageItems']:
            station = self.get_station_by_id(station_item['id'])
            if station.playable:
                self.fav_stations.append(station)

        logger.info('Radio.net: Loaded ' + str(len(self.fav_stations)) +
                    ' my stations.')

    def get_station_by_id(self, station_id):

        api_sufix = 'search/station'

        url_params = {
            'apikey': self.api_key,
            '_': self.current_milli_time(),
            'station': station_id,
        }

        response = self.do_get(api_sufix, url_params)

        if response.status_code is not 200:
            logger.error('Radio.net: Error on get station by id ' +
                         str(station_id) + ". Error: " + response.text)
            return False
        else:
            logger.debug('Radio.net: Done get top stations list')
            json = response.json()

            tmpStation = Station()
            tmpStation.id = json['id']
            tmpStation.continent = json['continent']
            tmpStation.country = json['country']
            tmpStation.city = json['city']
            tmpStation.genres = ', '.join(json["genres"])
            tmpStation.name = json['name']
            tmpStation.stream_url = self.__get_stream_url(
                json['streamUrls'], self.min_bitrate)
            tmpStation.image = json['logo300x300']
            tmpStation.description = json['shortDescription']
            if json['playable'] == 'PLAYABLE':
                tmpStation.playable = True

            return tmpStation

    def get_local_stations(self):
        self.local_stations = []

        api_sufix = 'search/localstations'

        url_params = {
            'apikey': self.api_key,
            '_': self.current_milli_time(),
            'pageindex': 1,
            'sizeperpage': 100,
        }

        response = self.do_post(api_sufix, url_params)

        if response.status_code is not 200:
            logger.error('Radio.net: Get local stations error. ' +
                         response.text)
        else:
            logger.debug('Radio.net: Done get local stations list')
            json = response.json()
            for match in json['categories'][0]['matches']:
                    station = self.get_station_by_id(match['id'])
                    if station:
                        if station.playable:
                            self.local_stations.append(station)

            logger.info('Radio.net: Loaded ' + str(len(self.local_stations)) +
                        ' local stations.')

    def get_top_stations(self):
        self.top_stations = []
        api_sufix = 'search/topstations'

        url_params = {
            'apikey': self.api_key,
            '_': self.current_milli_time(),
            'pageindex': 1,
            'sizeperpage': 100,
        }

        response = self.do_post(api_sufix, url_params)

        if response.status_code is not 200:
            logger.error('Radio.net: Get top stations error. ' + response.text)
        else:
            logger.debug('Radio.net: Done get top stations list')
            json = response.json()
            for match in json['categories'][0]['matches']:
                    station = self.get_station_by_id(match['id'])
                    if station:
                        if station.playable:
                            self.top_stations.append(station)

            logger.info('Radio.net: Loaded ' + str(len(self.top_stations)) +
                        ' top stations.')

    def do_search(self, query_string, page_index=1):
        if page_index == 1:
            self.search_results = []

        api_sufix = 'search/stationsonly'
        url_params = {
            'apikey': self.api_key,
            '_': self.current_milli_time(),
            'query': query_string,
            'pageindex': page_index,
        }

        response = self.do_post(api_sufix, url_params)

        if response.status_code is not 200:
            logger.error('Radio.net: Search error ' + response.text)
        else:
            logger.debug('Radio.net: Done search')
            json = response.json()
            for match in json['categories'][0]['matches']:
                    station = self.get_station_by_id(match['id'])
                    if station and station.playable:
                        self.search_results.append(station)

            number_pages = int(json['numberPages'])
            if number_pages >= page_index:
                self.do_search(query_string, page_index + 1)
            else:
                logger.info('Radio.net: Found ' +
                            str(len(self.search_results)) + ' stations.')
