# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: data_formats.py
# Project: core
# Author: Brian Cherinka
# Created: Tuesday, 23rd June 2020 4:41:31 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2020 Brian Cherinka
# Last Modified: Tuesday, 23rd June 2020 4:41:32 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
from astropy.table import Table
from astropy.utils.data import get_readable_fileobj

import jdaviz.core.data_identifiers as dataid
from jdaviz.core.config import list_configurations


class Base(object):
    @classmethod
    def register(cls):
        '''register the object in the format table '''
        return (cls.fname, cls.config, cls.dimension, cls.identifier)


class JWSTx1D(Base):
    fname = 'JWST x1d'
    config = 'specviz'
    dimension = '1d'
    identifier = 'identify_jwst_x1d_fits'


class BaseImage(Base):
    config = 'imviz'
    dimension = '2d'


class JWSTs2D(BaseImage):
    fname = 'JWST s2d'
    config = 'imviz'
    dimension = '2d'
    identifier = 'identify_jwst_s2d_fits'


class BaseCube(Base):
    config = 'cubeviz'
    dimension = '3d'


class JWSTs3D(BaseCube):
    fname = 'JWST s3d'
    identifier = 'identify_jwst_s3d_fits'


class MangaCube(BaseCube):
    fname = 'MaNGA cube'
    identifier = 'identify_sdss_manga_cube_fits'


# generic formats

class GenericCube(BaseCube):
    fname = 'generic cube'
    identifier = 'identify_generic_cube'


class GenericImage(BaseImage):
    fname = 'generic image'
    identifier = 'identify_generic_fits_image'


def _get_subclasses(base):
    ''' Recursively get all subclasses from a given base class '''
    subs = []
    for cls in base.__subclasses__():
        if cls.__subclasses__():
            subs.extend(_get_subclasses(cls))
        elif hasattr(cls, 'fname'):
            subs.append(cls)
        else:
            pass
    return subs


def get_formats():
    ''' Retrieve the registered list of valid jdaviz formats '''
    tt = Table(names=['format', 'config', 'dimension', 'identifier'],
               dtype=['str', 'str', 'str', 'str'])

    for cls in _get_subclasses(Base):
        tt.add_row(cls.register())

    tt.sort('format')

    return tt


def get_valid_format(filename):
    ''' Identify a best match jdaviz format from a filename '''

    # get a list of all valid formats
    formats = get_formats()

    # identify first available matching format
    valid_format = None
    config = None
    for row in formats:
        # lookup and call the identifier function
        assert hasattr(dataid, row["identifier"]), (f'Identifier {row["identifier"]} missing '
                                                    'definition in from list of functions.')

        idfxn = getattr(dataid, row["identifier"])
        if idfxn(filename):
            valid_format = row['format']
            config = row['config']
            break

    # return the format and config
    return valid_format, config


def identify_data(filename, current=None):
    ''' Identify the data format and application configuration from a filename '''

    valid_format, config = get_valid_format(filename)

    # get a list of pre-built configurations
    valid_configs = list_configurations()

    # - check that valid_format exists
    # - check that config is in the list of available configurations
    # - check that config does not conflict with the existing configuration

    if not valid_format:
        raise ValueError('Cannot determine the format of the file to load.  Please specify a format')
    elif config not in valid_configs:
        raise ValueError(f"Config {config} not a valid configuration.")
    elif current and config != current:
        raise ValueError('Mismatch between input file format and loaded configuration.')
    else:
        return valid_format, config

