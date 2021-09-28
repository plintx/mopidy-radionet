#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
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
    image_tiny = None
    image_small = None
    image_medium = None
    image_large = None
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
    favorites = []

    cache = {}

    stations_by_id = {}
    stations_by_slug = {}

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
        if lang == "en":
            lang = "net"
        langs = ["net", "de", "at", "fr", "pt", "es", "dk", "se", "it", "pl"]
        self.base_url = "https://radio.net/"
        if lang in langs:
            self.base_url = self.base_url.replace(".net", "." + lang)
        else:
            logging.warning("Radio.net not supported language: %s, defaulting to English", str(lang))
        self.update_prefix()

    def update_prefix(self):
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
        if not self.stations_by_id.get(station_id):
            return self._get_station_by_id(station_id)
        return self.stations_by_id.get(station_id)

    def get_station_by_slug(self, station_slug):
        if not self.stations_by_slug.get(station_slug):
            return self._get_station_by_id(station_slug)
        return self.stations_by_slug.get(station_slug)

    def _get_station_by_id(self, station_id):
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

        if not self.stations_by_id.get(json["id"]):
            station = Station()
            station.playable = True
        else:
            station = self.stations_by_id[json["id"]]
        station.id = json["id"]
        station.continent = json["continent"]
        station.country = json["country"]
        station.city = json["city"]
        station.genres = ", ".join(json["genres"])
        station.name = json["name"]
        station.slug = json["subdomain"]
        station.stream_url = self._get_stream_url(json["streamUrls"], self.min_bitrate)
        station.image_tiny = json["logo44x44"]
        station.image_small = json["logo100x100"]
        station.image_medium = json["logo175x175"]
        station.image_large = json["logo300x300"]
        station.description = json["shortDescription"]
        if json["playable"] == "PLAYABLE":
            station.playable = True

        self.stations_by_id[station.id] = station
        self.stations_by_slug[station.slug] = station

        self.set_cache("station/" + str(station.id), station, 1440)
        self.set_cache("station/" + station.slug, station, 1440)
        return station

    def _get_station_from_search_result(self, result):
        if not self.stations_by_id.get(result["id"]):
            station = Station()
            station.playable = True
        else:
            station = self.stations_by_id[result["id"]]

        station.id = result["id"]
        if result["continent"] is not None:
            station.continent = result["continent"]["value"]
        else:
            station.continent = ""

        if result["country"] is not None:
            station.country = result["country"]["value"]
        else:
            station.country = ""

        if result["city"] is not None:
            station.city = result["city"]["value"]
        else:
            station.city = ""

        if result["name"] is not None:
            station.name = result["name"]["value"]
        else:
            station.name = ""

        if result["subdomain"] is not None:
            station.slug = result["subdomain"]["value"]
        else:
            station.slug = ""

        if result["shortDescription"] is not None:
            station.description = result["shortDescription"]["value"]
        else:
            station.description = ""

        station.image_tiny = result["logo44x44"]
        station.image_small = result["logo100x100"]
        station.image_medium = result["logo175x175"]

        self.stations_by_id[station.id] = station
        self.stations_by_slug[station.slug] = station
        return station

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
        results = []
        for result in self._get_sorted_category(category, name, sorting, page):
            results.append(self._get_station_from_search_result(result))
        return results

    def _get_sorted_category(self, category, name, sorting, page):

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
        results = []
        for result in self._get_category(category, page):
            results.append(self._get_station_from_search_result(result))
        return results

    def _get_category(self, category, page):
        cache_key = category + "/" + str(page)
        cache = self.get_cache(cache_key)
        if cache is not None:
            return cache

        api_suffix = "/search/" + category
        url_params = {"sizeperpage": 50, "pageindex": page}

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
        cache_key = "favorites"
        cache = self.get_cache(cache_key)
        if cache is not None:
            return cache

        favorite_stations = []
        for station_slug in self.favorites:

            station = self.get_station_by_slug(station_slug)

            if station is False:
                api_suffix = "/search/stationsonly"
                url_params = {
                    "query": station_slug,
                    "pageindex": 1,
                }
                response = self.do_get(api_suffix, url_params)

                if response.status_code != 200:
                    logger.error("Radio.net: Search error " + response.text)
                else:
                    logger.debug("Radio.net: Done search")
                    json = response.json()

                    number_pages = int(json["numberPages"])
                    logger.error(json)
                    if number_pages != 0:
                        # take only the first match!
                        station = self._get_station_from_search_result(
                            json["categories"][0]["matches"][0]
                        )
                    else:
                        logger.warning("Radio.net: No results for %s", station_slug)

            if station and station.playable:
                favorite_stations.append(station)

        logger.info(
            "Radio.net: Loaded " + str(len(favorite_stations)) + " favorite stations."
        )
        return self.set_cache(cache_key, favorite_stations, 1440)

    def do_search(self, query_string, page_index=1, search_results=None):

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
            if search_results is None:
                search_results = []
            json = response.json()
            for match in json["categories"][0]["matches"]:
                station = self._get_station_from_search_result(match)
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

    def get_stream_url(self, station_id):
        station = self.get_station_by_id(station_id)
        if not station.stream_url:
            station = self._get_station_by_id(station.id)
        return station.stream_url

    def _get_stream_url(self, stream_json, bit_rate):
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
        self._expires = time.time() + expires * 60

    def expired(self):
        return self._expires < time.time()

    def value(self):
        return self._value
