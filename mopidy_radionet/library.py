from __future__ import unicode_literals

import logging
import re

from mopidy import backend
from mopidy.models import Album, Artist, Ref, SearchResult, Track

logger = logging.getLogger(__name__)


class RadioNetLibraryProvider(backend.LibraryProvider):
    root_directory = Ref.directory(uri="radionet:root", name="Radio.net")

    def __init__(self, backend):
        super().__init__(backend)

    def lookup(self, uri):

        if not uri.startswith("radionet:"):
            return None

        variant, identifier, sorting, page = self.parse_uri(uri)

        if variant == "station" or variant == "track":
            identifier = int(identifier)
            radio_data = self.backend.radionet.get_station_by_id(identifier)

            artist = Artist(name=radio_data.name)

            name = ""
            if radio_data.description is not None:
                name = radio_data.description + " / "
            name = (
                name
                + radio_data.continent
                + " / "
                + radio_data.country
                + " - "
                + radio_data.city
            )

            album = Album(
                artists=[artist],
                name=name,
                uri="radionet:station:%s" % (identifier),
            )

            track = Track(
                artists=[artist],
                album=album,
                name=radio_data.name,
                genre=radio_data.genres,
                comment=radio_data.description,
                uri="radionet:track:%s" % (identifier),
            )
            return [track]

        return []

    def browse(self, uri):

        category, page, value, sorting = self.parse_uri(uri)

        if category == "root":
            return self._browse_root()
        elif category in ["favorites", "topstations", "localstations"]:
            return self._browse_category(category, page)
        elif category in ["genres", "topics", "languages", "cities", "countries"]:
            return self._browse_sorted_category(category, value, sorting, page)
        else:
            logger.debug("Unknown URI: %s", uri)
            return []

    def _browse_root(self):
        directories = [
            self.ref_directory("radionet:favorites", "Favorites"),
            self.ref_directory("radionet:topstations", "Top stations"),
            self.ref_directory("radionet:localstations", "Local stations"),
            self.ref_directory("radionet:genres", "Genres"),
            self.ref_directory("radionet:topics", "Topics"),
            self.ref_directory("radionet:languages", "Languages"),
            self.ref_directory("radionet:cities", "Cities"),
            self.ref_directory("radionet:countries", "Countries"),
        ]
        return directories

    def _browse_category(self, category, page):
        result = []
        if category == "favorites":
            items = self._get_favorites()
            if items:
                for item in items:
                    result.append(self.station_to_ref(item))
        elif category == "topstations":
            items = self._get_topstations()
            if items:
                for item in items:
                    result.append(self.station_to_ref(item))
        elif not page:
            pages = self._get_category_pages(category)
            if pages == 1:
                items = self._get_category(category, 1)
                if items:
                    for item in items:
                        result.append(self.station_to_ref(item))
            else:
                for index in range(pages):
                    result.append(
                        self.ref_directory(
                            "radionet:{0}:{1}".format(category, str(index + 1)),
                            str(index + 1),
                        )
                    )
        else:
            items = self._get_category(category, page)
            if items:
                for item in items:
                    result.append(self.station_to_ref(item))
        return result

    def _browse_sorted_category(self, category, value, sorting, page):
        result = []

        if not value:
            items = self.__getattribute__("_get_{0}".format(category))()
            if items:
                for item in items:
                    result.append(
                        self.ref_directory(
                            "radionet:{0}:{1}".format(category, item["systemEnglish"]),
                            item["localized"],
                        )
                    )
        elif not sorting or sorting not in ["rank", "az"]:
            result.append(
                self.ref_directory(
                    "radionet:{0}:{1}:rank".format(category, value), "By rank"
                )
            )
            result.append(
                self.ref_directory(
                    "radionet:{0}:{1}:az".format(category, value), "Alphabetical"
                )
            )
        elif not page:
            pages = self._get_sorted_category_pages(category, value)
            if pages == 1:
                items = self._get_sorted_category(category, value, sorting, 1)
                if items:
                    for item in items:
                        result.append(self.station_to_ref(item))
            else:
                for index in range(pages):
                    result.append(
                        self.ref_directory(
                            "radionet:{0}:{1}:{2}:{3}".format(
                                category, value, sorting, str(index + 1)
                            ),
                            str(index + 1),
                        )
                    )
        else:
            items = self._get_sorted_category(category, value, sorting, page)
            if items:
                for item in items:
                    result.append(self.station_to_ref(item))
        return result

    def _get_genres(self):
        return self.backend.radionet.get_genres()

    def _get_topics(self):
        return self.backend.radionet.get_topics()

    def _get_languages(self):
        return self.backend.radionet.get_languages()

    def _get_cities(self):
        return self.backend.radionet.get_cities()

    def _get_countries(self):
        return self.backend.radionet.get_countries()

    def _get_topstations(self):
        return self.backend.radionet.get_category("topstations", 1)

    def _get_sorted_category(self, category, name, sorting, page):
        return self.backend.radionet.get_sorted_category(category, name, sorting, page)

    def _get_sorted_category_pages(self, category, name):
        return self.backend.radionet.get_sorted_category_pages(category, name)

    def _get_category(self, category, page):
        return self.backend.radionet.get_category(category, page)

    def _get_category_pages(self, category):
        return self.backend.radionet.get_category_pages(category)

    def _get_favorites(self):
        return self.backend.radionet.get_favorites()

    def search(self, query=None, uris=None, exact=False):
        if "any" not in query:
            return None

        result = []

        for station in self.backend.radionet.do_search(" ".join(query["any"])):
            result.append(self.station_to_track(station))

        return SearchResult(tracks=result)

    def station_to_ref(self, station):
        return Ref.track(
            uri="radionet:station:%s" % (station.id),
            name=station.name,
        )

    def station_to_track(self, station):
        ref = self.station_to_ref(station)
        return Track(
            uri=ref.uri,
            name=ref.name,
            album=Album(uri=ref.uri, name=ref.name),
            artists=[Artist(uri=ref.uri, name=ref.name)],
        )

    def ref_directory(self, uri, name):
        return Ref.directory(uri=uri, name=name)

    def ref_track(self, uri, name):
        return Ref.track(uri=uri, name=name)

    def parse_uri(self, uri):
        category = None
        value = None
        page = None
        sorting = None

        result = re.findall(
            r"^radionet:(genres|topics|languages|cities|countries)(:([^:]+)(:(rank|az)(:([0-9]+))?)?)?$",
            uri,
        )

        if result:
            category = result[0][0]
            value = result[0][2]
            sorting = result[0][4]
            page = result[0][6]

        else:
            result = re.findall(
                r"^radionet:(root|favorites|topstations|localstations|station|track)(:([0-9]+))?$",
                uri,
            )

            if result:
                category = result[0][0]
                page = result[0][2]

        return category, page, value, sorting
