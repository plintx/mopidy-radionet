****************************
Mopidy-RadioNet
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-RadioNet.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-RadioNet/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/travis/blackberrymamba/mopidy-radionet/master.svg?style=flat
    :target: https://travis-ci.org/blackberrymamba/mopidy-radionet
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/blackberrymamba/mopidy-radionet/master.svg?style=flat
   :target: https://coveralls.io/r/blackberrymamba/mopidy-radionet
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

v0.1.0 (UNRELEASED)
----------------------------------------

- Initial release.
