from __future__ import unicode_literals

import time

from mopidy import backend

import pykka

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

        self.uri_schemes = ['radionet']
        self.username = config['radionet']['username']
        self.password = config['radionet']['password']

        self.radionet.min_bitrate = int(config['radionet']['min_bitrate'])
        self.radionet.set_lang(str(config['radionet']['language']))

    def set_update_timeout(self, minutes=2):
        self.update_timeout = time.time() + 60 * minutes

    def on_start(self):
        self.set_update_timeout(0)

    def refresh(self, force=False):
        if self.update_timeout is None:
            self.set_update_timeout()

        if force or time.time() > self.update_timeout:
            self.radionet.login(self.username, self.password)
            self.radionet.get_bookmarks()
            self.radionet.get_my_stations_streams()
            self.radionet.get_top_stations()
            self.radionet.get_local_stations()
            self.set_update_timeout()
