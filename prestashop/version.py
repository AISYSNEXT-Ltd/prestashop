# -*- coding: utf-8 -*-

try:
    from importlib.metadata import PackageNotFoundError,version
    __version__ = version('prestashop')
except PackageNotFoundError:
    __version__ = '0.1.0'

__author__= "Aymen Jemi <jemiaymen@gmail.com> (AISYSNEXT)"
