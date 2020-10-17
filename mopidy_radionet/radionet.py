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

    session = requests.Session()
    api_key = None
    api_prefix = None
    min_bitrate = 96
    max_top_stations = 100
    station_bookmarks = None

    stations_images = []
    top_stations = []
    local_stations = []
    search_results = []

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
        else:
            logging.error("Radio.net not supported language: %s", str(lang))

    def flush(self):
        self.top_stations = []
        self.local_stations = []
        self.search_results = []

    def current_milli_time(self):
        return int(round(time.time() * 1000))

    def get_api_key(self):
        if self.api_key is not None:
            return

        tmp_str = self.session.get(self.base_url)

        apiprefix_search = re.search('apiPrefix ?: ?\'(.*)\',?', tmp_str.content.decode())
        self.api_prefix = apiprefix_search.group(1)

        apikey_search = re.search('apiKey ?: ?[\'|"](.*)[\'|"],?', tmp_str.content.decode())
        self.api_key = apikey_search.group(1)

        logger.info('Radio.net: APIPREFIX %s' % self.api_prefix)
        logger.info('Radio.net: APIKEY %s' % self.api_key)

    def do_post(self, api_sufix, url_params=None, payload=None):
        self.get_api_key()

        if 'apikey' in url_params.keys():
            url_params['apikey'] = self.api_key

        response = self.session.post(self.api_prefix + api_sufix,
                                     params=url_params, data=payload)

        return response

    def do_get(self, api_sufix, url_params=None):
        self.get_api_key()

        if 'apikey' in url_params.keys():
            url_params['apikey'] = self.api_key

        response = self.session.get(self.api_prefix + api_sufix,
                                    params=url_params)

        return response

    def get_station_by_id(self, station_id):

        api_suffix = '/search/station'

        url_params = {
            'apikey': self.api_key,
            '_': self.current_milli_time(),
            'station': station_id,
        }

        response = self.do_get(api_suffix, url_params)

        if response.status_code is not 200:
            logger.error('Radio.net: Error on get station by id ' +
                         str(station_id) + ". Error: " + response.text)
            return False
        else:
            logger.debug('Radio.net: Done get top stations list')
            json = response.json()

            station = Station()
            station.id = json['id']
            station.continent = json['continent']
            station.country = json['country']
            station.city = json['city']
            station.genres = ', '.join(json["genres"])
            station.name = json['name']
            station.stream_url = self.get_stream_url(
                json['streamUrls'], self.min_bitrate)
            station.image = json['logo100x100']
            station.description = json['shortDescription']
            if json['playable'] == 'PLAYABLE':
                station.playable = True

            return station

    def get_local_stations(self):
        self.local_stations = []

        api_suffix = '/search/localstations'

        url_params = {
            'apikey': self.api_key,
            '_': self.current_milli_time(),
            'pageindex': 1,
            'sizeperpage': 100,
        }

        response = self.do_post(api_suffix, url_params)

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
        api_suffix = '/search/topstations'

        url_params = {
            'apikey': self.api_key,
            '_': self.current_milli_time(),
            'pageindex': 1,
            'sizeperpage': 100,
        }

        response = self.do_post(api_suffix, url_params)

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

        api_suffix = '/search/stationsonly'
        url_params = {
            'apikey': self.api_key,
            '_': self.current_milli_time(),
            'query': query_string,
            'pageindex': page_index,
        }

        response = self.do_post(api_suffix, url_params)

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

    def get_stream_url(self, stream_json, bit_rate):
        stream_url = None

        for stream in stream_json:
            if int(stream['bitRate']) >= bit_rate and \
                    stream['streamStatus'] == 'VALID':
                stream_url = stream['streamUrl']
                break

        if stream_url is None and len(stream_json) > 0:
            stream_url = stream_json[0]['streamUrl']

        return stream_url
