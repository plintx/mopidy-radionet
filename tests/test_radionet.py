import unittest

from mopidy_radionet.radionet import RadioNetClient


class RadioNetClientTest(unittest.TestCase):

    def test_get_api_key(self):
        radionet = RadioNetClient()
        radionet.get_api_key()

        self.assertIsNotNone(radionet.api_key)

    def test_get_top_stations(self):
        radionet = RadioNetClient()
        radionet.get_top_stations()
        self.assertGreater(len(radionet.top_stations), 0)

    def test_get_local_stations(self):
        radionet = RadioNetClient()
        radionet.get_local_stations()
        self.assertGreater(len(radionet.local_stations), 0)

    def test_do_search(self):
        radionet = RadioNetClient()
        radionet.do_search("radio ram")
        self.assertGreater(len(radionet.search_results), 0)

    def test_get_favorites(self):
        test_favorites = ("Rock Antenne", "radio ram")
        radionet = RadioNetClient()
        radionet.set_favorites(test_favorites)
        radionet.get_favorites()
        self.assertEqual(len(radionet.favorite_stations), len(test_favorites))


if __name__ == "__main__":
    unittest.main()
