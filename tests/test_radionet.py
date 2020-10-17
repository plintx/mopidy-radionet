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


if __name__ == "__main__":
    unittest.main()
