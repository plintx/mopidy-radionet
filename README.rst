****************************
Mopidy-RadioNet
****************************

Mopidy extension for radio.net


Installation
============

Install by running::

    pip install Mopidy-RadioNet

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.


Configuration
=============

Before starting Mopidy, you must add configuration for
Mopidy-RadioNet to your Mopidy configuration file::

    [radionet]
    enabled = true
    username = alice666.9
    password = secret
    language = pl # or net, de, at, fr, pt, es, dk, se, it
    min_bitrate = 96


Project resources
=================

- `Source code <https://github.com/blackberrymamba/mopidy-radionet>`_
- `Issue tracker <https://github.com/blackberrymamba/mopidy-radionet/issues>`_


Changelog
=========
v0.2.0 Python 3
----------------------------------------

- Migration to Python 3.7

v0.1.0 (UNRELEASED)
----------------------------------------

- Initial release.
