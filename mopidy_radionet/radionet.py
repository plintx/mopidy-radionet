#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import re
import time

import requests
from mopidy import httpclient

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
    base_url = "https://radio.net/"

    session = requests.Session()
    api_prefix = None
    min_bitrate = 96
    max_top_stations = 100
    station_bookmarks = None
    api_key = None

    stations_images = []
    search_results = []
    favorites = []
    cache = {}

    category_param_map = {
        "genres": "genre",
        "topics": "topic",
        "languages": "language",
        "cities": "city",
        "countries": "country",
    }

    def __init__(self, proxy_config=None, user_agent=None):
        super(RadioNetClient, self).__init__()

        self.session = requests.Session()

        if proxy_config is not None:
            proxy = httpclient.format_proxy(proxy_config)
            self.session.proxies.update({"http": proxy, "https": proxy})

        full_user_agent = httpclient.format_user_agent(user_agent)
        self.session.headers.update({"user-agent": full_user_agent})
        self.session.headers.update({"cache-control": "no-cache"})

        self.update_prefix()

    def __del__(self):
        self.session.close()

    def set_lang(self, lang):
        langs = ["net", "de", "at", "fr", "pt", "es", "dk", "se", "it", "pl"]
        if lang in langs:
            self.base_url = self.base_url.replace(".net", "." + lang)
        else:
            logging.error("Radio.net not supported language: %s", str(lang))
        self.update_prefix()

    def update_prefix(self):
        tmp_str = self.session.get(self.base_url)
        lang = self.base_url.split(".")[-1].replace("/", "")
        self.api_prefix = "https://api.radio." + lang + "/info/v2"

    def set_apikey(self, api_key):
        self.api_key = api_key

    def do_get(self, api_suffix, url_params=None):
        if self.api_prefix is None:
            return None

        if url_params is None:
            url_params = {}
        url_params["apikey"] = self.api_key

        response = self.session.get(self.api_prefix + api_suffix, params=url_params)

        return response

    def get_cache(self, key):
        if self.cache.get(key) is not None and self.cache[key].expired() is False:
            return self.cache[key].value()
        return None

    def set_cache(self, key, value, expires):
        self.cache[key] = CacheItem(value, expires)
        return value

    def get_station_by_id(self, station_id):
        cache_key = "station/" + str(station_id)
        cache = self.get_cache(cache_key)
        if cache is not None:
            return cache

        api_suffix = "/search/station"

        url_params = {
            "station": station_id,
        }

        response = self.do_get(api_suffix, url_params)

        if response.status_code != 200:
            logger.error(
                "Radio.net: Error on get station by id "
                + str(station_id)
                + ". Error: "
                + response.text
            )
            return False

        logger.debug("Radio.net: Done get top stations list")
        json = response.json()

        station = Station()
        station.id = json["id"]
        station.continent = json["continent"]
        station.country = json["country"]
        station.city = json["city"]
        station.genres = ", ".join(json["genres"])
        station.name = json["name"]
        station.stream_url = self.get_stream_url(json["streamUrls"], self.min_bitrate)
        station.image = json["logo100x100"]
        station.description = json["shortDescription"]
        if json["playable"] == "PLAYABLE":
            station.playable = True

        return self.set_cache(cache_key, station, 1440)

    def get_genres(self):
        return self._get_items("genres")

    def get_topics(self):
        return self._get_items("topics")

    def get_languages(self):
        return self._get_items("languages")

    def get_cities(self):
        return self._get_items("cities")

    def get_countries(self):
        return self._get_items("countries")

    def _get_items(self, key):
        cached = self.get_cache(key)
        if cached is not None:
            return cached

        api_suffix = "/search/get" + key
        response = self.do_get(api_suffix)
        if response.status_code != 200:
            logger.error(
                "Radio.net: Error on get item list "
                + str(api_suffix)
                + ". Error: "
                + response.text
            )
            return False
        return self.set_cache(key, response.json(), 1440)

    def get_sorted_category(self, category, name, sorting, page):

        if sorting == "az":
            sorting = "STATION_NAME"
        else:
            sorting = "RANK"

        cache_key = category + "/" + name + "/" + sorting + "/" + str(page)
        cache = self.get_cache(cache_key)
        if cache is not None:
            return cache

        api_suffix = "/search/stationsby" + self.category_param_map[category]
        url_params = {
            self.category_param_map[category]: name,
            "sorttype": sorting,
            "sizeperpage": 50,
            "pageindex": page,
        }

        response = self.do_get(api_suffix, url_params)

        if response.status_code != 200:
            logger.error(
                "Radio.net: Error on get station by "
                + str(category)
                + ". Error: "
                + response.text
            )
            return False

        json = response.json()
        self.set_cache(category + "/" + name, int(json["numberPages"]), 10)
        return self.set_cache(cache_key, json["categories"][0]["matches"], 10)

    def get_category(self, category, page):
        cache_key = category + "/" + str(page)
        cache = self.get_cache(cache_key)
        if cache is not None:
            return cache

        api_suffix = "/search/" + category
        url_params = {"sizeperpage": 50, "pageindex": page}

        response = self.do_get(api_suffix, url_params)
        logger.error(response.text)
        if response.status_code != 200:
            logger.error(
                "Radio.net: Error on get station by "
                + str(category)
                + ". Error: "
                + response.text
            )
            return False

        json = response.json()
        self.set_cache(category, int(json["numberPages"]), 10)
        return self.set_cache(cache_key, json["categories"][0]["matches"], 10)

    def get_sorted_category_pages(self, category, name):
        cache_key = category + "/" + name
        cache = self.get_cache(cache_key)
        if cache is not None:
            return cache

        self.get_sorted_category(category, name, "rank", 1)

        return self.get_cache(cache_key)

    def get_category_pages(self, category):
        cache_key = category
        cache = self.get_cache(cache_key)
        if cache is not None:
            return cache

        self.get_category(category, 1)

        return self.get_cache(cache_key)

    def set_favorites(self, favorites):
        self.favorites = favorites

    def get_favorites(self):
        logger.error(str(self.favorites))
        cache_key = "favorites"
        cache = self.get_cache(cache_key)
        if cache is not None:
            return cache

        favorite_stations = []
        for station in self.favorites:
            logger.error(str(station))
            api_suffix = "/search/stationsonly"
            url_params = {
                "query": station,
                "pageindex": 1,
            }
            response = self.do_get(api_suffix, url_params)

            if response.status_code != 200:
                logger.error("Radio.net: Search error " + response.text)
            else:
                logger.debug("Radio.net: Done search")
                json = response.json()

                # take only the first match!
                station = self.get_station_by_id(
                    json["categories"][0]["matches"][0]["id"]
                )
                if station and station.playable:
                    favorite_stations.append(station)

        logger.info(
            "Radio.net: Loaded " + str(len(favorite_stations)) + " favorite stations."
        )
        return self.set_cache(cache_key, favorite_stations, 1440)

    def do_search(self, query_string, page_index=1, search_results=[]):

        api_suffix = "/search/stationsonly"
        url_params = {
            "query": query_string,
            "sizeperpage": 50,
            "pageindex": page_index,
        }

        response = self.do_get(api_suffix, url_params)

        if response.status_code != 200:
            logger.error("Radio.net: Search error " + response.text)
        else:
            logger.debug("Radio.net: Done search")
            json = response.json()
            for match in json["categories"][0]["matches"]:
                station = self.get_station_by_id(match["id"])
                if station and station.playable:
                    search_results.append(station)

            number_pages = int(json["numberPages"])
            if number_pages >= page_index:
                self.do_search(query_string, page_index + 1, search_results)
            else:
                logger.info(
                    "Radio.net: Found " + str(len(search_results)) + " stations."
                )
        return search_results

    def get_stream_url(self, stream_json, bit_rate):
        stream_url = None

        for stream in stream_json:
            if int(stream["bitRate"]) >= bit_rate and stream["streamStatus"] == "VALID":
                stream_url = stream["streamUrl"]
                break

        if stream_url is None and len(stream_json) > 0:
            stream_url = stream_json[0]["streamUrl"]

        return stream_url


class CacheItem(object):
    def __init__(self, value, expires=10):
        self._value = value
        self._expires = expires = time.time() + expires * 60

    def expired(self):
        return self._expires < time.time()

    def value(self):
        return self._value
