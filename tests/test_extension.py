from __future__ import unicode_literals

from mopidy_radionet import Extension


def test_get_default_config():
    ext = Extension()

    config = ext.get_default_config()

    assert '[radionet]' in config
    assert 'enabled = true' in config


def test_get_config_schema():
    ext = Extension()

    schema = ext.get_config_schema()

    assert 'username' in schema
    assert 'password' in schema
    assert 'language' in schema
    assert 'min_bitrate' in schema
