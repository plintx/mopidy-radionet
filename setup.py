from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    with open(filename) as fh:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fh.read()))
        return metadata['version']


setup(
    name='Mopidy-RadioNet',
    version=get_version('mopidy_radionet/__init__.py'),
    url='https://github.com/plintx/mopidy-radionet',
    license='Apache License, Version 2.0',
    author='plintx',
    author_email='mariusz@intx.pl',
    description='Mopidy extension for radio.net',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    python_requires='>= 3.7',
    install_requires=[
        'Mopidy >= 3.0.0',
        'Pykka >= 2.0.1',
        'setuptools',
        'uritools >= 1.0'
    ],
    entry_points={
        'mopidy.ext': [
            'radionet = mopidy_radionet:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
