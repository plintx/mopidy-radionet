from unittest import mock

import pytest

from mopidy_radionet import backend
from mopidy_radionet.radionet import RadioNetClient
from mopidy_radionet.library import RadioNetLibraryProvider


@pytest.fixture
def backend_mock():
    backend_mock = mock.Mock(spec=backend.RadioNetBackend)
    backend_mock.radionet = RadioNetClient(proxy_config=None)
    backend_mock.library = RadioNetLibraryProvider(backend=backend_mock)
    backend_mock.radionet.set_apikey('test')
    backend_mock.radionet.set_favorites({'lush'})
    return backend_mock


@pytest.fixture
def library(backend_mock):
    return backend_mock.library


@pytest.fixture
def radionet(backend_mock):
    return backend_mock.radionet
