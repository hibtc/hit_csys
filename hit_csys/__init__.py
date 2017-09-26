# encoding: utf-8
"""
Python API for talking to the HIT online control/DVM.
"""

from __future__ import unicode_literals


__title__ = 'hit_csys'
__summary__ = 'Online control for the HIT accelerator facility.'
__uri__ = 'https://bitbucket.org/coldfix/hit-online-control'

__version__ = '0.3.1'

__author__ = 'Thomas Gläßle'
__email__ = 't_glaessle@gmx.de'

__license__ = None
__copyright__ = '(C) 2013 - 2015 HIT Betriebs GmbH'

# Trove classifiers: https://pypi.python.org/pypi?:action=list_classifiers
__classifiers__ = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Healthcare Industry',
    'Intended Audience :: Science/Research',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Medical Science Apps.',
    'Topic :: Scientific/Engineering :: Physics',
]

entry_points = """
[madqt.online.PluginLoader]
stub = hit_csys.plugin:StubLoader
dll = hit_csys.plugin:DllLoader
"""