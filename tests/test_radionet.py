from unittest import mock


def test_get_genres(radionet):
    genres = radionet.get_genres();
    assert len(genres) > 0


def test_get_top_stations(radionet):
    result = radionet.get_category('topstations', 1)
    assert len(result) > 0


def test_get_local_stations(radionet):
    result = radionet.get_category('localstations', 1)
    assert len(result) > 0


def test_do_search(radionet):
    result = radionet.do_search("radio ram")
    assert len(result) > 0

    assert result[0].stream_url is None

    assert radionet.get_stream_url(result[0].id) is not None


def test_get_favorites(radionet):
    test_favorites = ("Rock Antenne", "radio ram", "eska", "dancefm")
    radionet.set_favorites(test_favorites)
    result = radionet.get_favorites()
    assert len(result) == len(test_favorites)

    assert result[2].name == 'Eska'
