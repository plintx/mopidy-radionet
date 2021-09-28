from unittest import mock


def test_browse_root(library):
    results = library.browse('radionet:root');
    assert 8 == len(results)


def test_browse_localstations(library):
    results = library.browse('radionet:localstations');
    assert len(results) > 0

    page_uri = results[0].uri if results is not None else None
    assert page_uri is not None

    # 1 Page, not results
    # results = library.browse(page_uri)
    # assert len(results) > 0


def test_browse_topstations(library):
    results = library.browse('radionet:topstations');
    assert len(results) > 0


def test_browse_genres(library):
    results = library.browse('radionet:genres');
    assert len(results) > 0

    cat_uri = results[0].uri if results is not None else None
    assert cat_uri is not None

    results = library.browse(cat_uri)
    assert len(results) == 2

    sort_uri = results[0].uri if results is not None else None
    assert sort_uri is not None

    results = library.browse(sort_uri)
    assert len(results) > 0

    page_uri = results[0].uri if results is not None else None
    assert page_uri is not None

    results = library.browse(page_uri)
    assert len(results) > 0


def test_browse_topics(library):
    results = library.browse('radionet:topics');
    assert len(results) > 0

    cat_uri = results[0].uri if results is not None else None
    assert cat_uri is not None

    results = library.browse(cat_uri)
    assert len(results) == 2

    sort_uri = results[0].uri if results is not None else None
    assert sort_uri is not None

    results = library.browse(sort_uri)
    assert len(results) > 0

    page_uri = results[0].uri if results is not None else None
    assert page_uri is not None

    # 1 Page, not results
    # results = library.browse(page_uri)
    # assert len(results) > 0


def test_browse_languages(library):
    results = library.browse('radionet:languages');
    assert len(results) > 0

    cat_uri = results[5].uri if results is not None else None
    assert cat_uri is not None

    results = library.browse(cat_uri)
    assert len(results) == 2

    sort_uri = results[0].uri if results is not None else None
    assert sort_uri is not None

    results = library.browse(sort_uri)
    assert len(results) > 0

    page_uri = results[0].uri if results is not None else None
    assert page_uri is not None

    # 1 Page, not results
    # results = library.browse(page_uri)
    # assert len(results) > 0


def test_browse_cities(library):
    results = library.browse('radionet:cities');
    assert len(results) > 0

    cat_uri = results[0].uri if results is not None else None
    assert cat_uri is not None

    results = library.browse(cat_uri)
    assert len(results) == 2

    sort_uri = results[0].uri if results is not None else None
    assert sort_uri is not None

    results = library.browse(sort_uri)
    assert len(results) > 0

    page_uri = results[0].uri if results is not None else None
    assert page_uri is not None

    # 1 Page, not results
    # results = library.browse(page_uri)
    # assert len(results) > 0


def test_browse_countries(library):
    results = library.browse('radionet:countries');
    assert len(results) > 0

    cat_uri = results[0].uri if results is not None else None
    assert cat_uri is not None

    results = library.browse(cat_uri)
    assert len(results) == 2

    sort_uri = results[0].uri if results is not None else None
    assert sort_uri is not None

    results = library.browse(sort_uri)
    assert len(results) > 0

    page_uri = results[0].uri if results is not None else None
    assert page_uri is not None

    # 1 Page, not results
    # results = library.browse(page_uri)
    # assert len(results) > 0


def test_browse_favorites(library):
    results = library.browse('radionet:favorites');
    assert 1 == len(results)



def test_search(library):
    result = library.search({'any': ['radio ram']})

    assert len(result.tracks) > 0

    old_length = len(result.tracks)

    result = library.search({'any': ['radio ram']})

    assert len(result.tracks) == old_length


def test_lookup(library):

    results = library.browse('radionet:favorites')
    assert 1 == len(results)

    for result in results:
        assert library.lookup(result.uri) is not None


def test_track_by_slug(library):

    results = library.lookup('radionet:track:dancefm')
    assert 1 == len(results)
    assert results[0].uri == 'radionet:track:2180'
