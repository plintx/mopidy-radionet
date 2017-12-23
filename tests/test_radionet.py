import unittest

from mopidy_radionet.radionet import RadioNetClient


class RadioNetClientTest(unittest.TestCase):

    username = 'alice666.9'
    password = 'secret'

    def test_get_api_key(self):
        radionet = RadioNetClient()
        radionet.get_api_key()

        self.assertIsNotNone(radionet.api_key)

    def test_login(self):
        radionet = RadioNetClient()
        radionet.login(self.username, self.password)
        self.assertEqual(radionet.user_login, self.username)

    def test_get_bookmarks(self):
        radionet = RadioNetClient()
        radionet.login(self.username, self.password)
        radionet.get_bookmarks()
        self.assertIsNotNone(radionet.station_bookmarks)

    def test_get_bookmarks_station_streams(self):
        radionet = RadioNetClient()
        radionet.login(self.username, self.password)
        radionet.get_bookmarks()
        radionet.get_my_stations_streams()
        self.assertGreater(len(radionet.fav_stations), 0)

    def test_get_top_stations(self):
        radionet = RadioNetClient()
        radionet.login(self.username, self.password)
        radionet.get_top_stations()
        self.assertGreater(len(radionet.top_stations), 0)

    def test_get_local_stations(self):
        radionet = RadioNetClient()
        radionet.login(self.username, self.password)
        radionet.get_local_stations()
        self.assertGreater(len(radionet.local_stations), 0)

    def test_do_search(self):
        radionet = RadioNetClient()
        radionet.login(self.username, self.password)
        radionet.do_search("radio ram")
        self.assertGreater(len(radionet.search_results), 0)


if __name__ == "__main__":
    unittest.main()
