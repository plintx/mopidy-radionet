****************************
Mopidy-RadioNet
****************************
.. image:: https://img.shields.io/pypi/v/Mopidy-RadioNet.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-RadioNet/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/travis/plintx/mopidy-radionet/master.svg?style=flat
    :target: https://travis-ci.org/plintx/mopidy-radionet
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/plintx/mopidy-radionet/master.svg?style=flat
   :target: https://coveralls.io/r/plintx/mopidy-radionet
   :alt: Test coverage

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
    language = pl # or net, de, at, fr, pt, es, dk, se, it
    min_bitrate = 96
    favorite_stations =
      'bbcradio1'
      'bbcradio2'
      'thetrip'
      'nectarine'
      
* `enabled` determines whether the plugin is enabled. Disabling the
  plugin is a simple case of changing this to `false` and restarting
  Mopidy.

* `language` determines the language of text information such at station
  descriptions. The following options are:
  * net - defaults to English
  * at  - Austrian
  * de  - German
  * dk  - Danish
  * es  - Spanish
  * fr  - French
  * it  - Italian
  * pl  - Polish
  * pt  - Portuguese
  * se  - Swedish
  
* `min_bitrate` sets the minimum desirable bitrate of streams. Typically
  higher bitrates mean better quality (or at least, that's the idea),
  but take up more bandwidth. If your stream of choice keeps halting, it
  might help to turn this down a little.
  
* `favorite_stations` lets you define a list of your favorite stations
  for quick access. To add a station to the list, you need to add its
  slug, the part that comes after the domain name in the station's URL.
  As an example, BBC Radio 1 can be found at `radio.net/s/bbcradio1`.
  Therefore, to add the station to your favourites, you would take the
  part after the final forward slash - `bbcradio1` - and add that to
  `favorite_stations`

Project resources
=================

- `Source code <https://github.com/blackberrymamba/mopidy-radionet>`_
- `Issue tracker <https://github.com/blackberrymamba/mopidy-radionet/issues>`_


Changelog
=========

v0.2.1 Changes in radio.net
----------------------------------------

v0.2.0 Python 3
----------------------------------------

- Migration to Python 3.7

v0.1.0 (UNRELEASED)
----------------------------------------

- Initial release.
