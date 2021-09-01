from __future__ import unicode_literals

import time

from mopidy import backend

import pykka
import re

import mopidy_radionet

from .library import RadioNetLibraryProvider
from .radionet import RadioNetClient


class RadioNetBackend(pykka.ThreadingActor, backend.Backend):
    update_timeout = None

    def __init__(self, config, audio):
        super(RadioNetBackend, self).__init__()
        self.radionet = RadioNetClient(
            config['proxy'],
            "%s/%s" % (
                mopidy_radionet.Extension.dist_name,
                mopidy_radionet.__version__))

        self.library = RadioNetLibraryProvider(backend=self)
        self.playback = RadioNetPlaybackProvider(
            audio=audio, backend=self
        )

        self.uri_schemes = ['radionet']

        self.radionet.min_bitrate = int(config['radionet']['min_bitrate'])
        self.radionet.set_lang(str(config['radionet']['language']))
        self.radionet.set_favorites(tuple(file_ext.lower() for file_ext in config["radionet"]["favorite_stations"]))

    def set_update_timeout(self, minutes=2):
        self.update_timeout = time.time() + 60 * minutes

    def on_start(self):
        self.set_update_timeout(0)

    def refresh(self, force=False):
        if self.update_timeout is None:
            self.set_update_timeout()

        if force or time.time() > self.update_timeout:
            self.radionet.get_top_stations()
            self.radionet.get_local_stations()
            self.radionet.get_favorites()
            self.set_update_timeout()

class RadioNetPlaybackProvider(backend.PlaybackProvider):

    def is_live(self, uri):
        return True

    def translate_uri(self, uri):
        identifier = re.findall(r'^radionet:track:?([a-z0-9]+|\d+)?$', uri)
        if identifier:
            radio_data = self.backend.radionet.get_station_by_id(identifier)
            if radio_data:
                return radio_data.stream_url

        return None