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
from functools import wraps

from astropy.table import Table
from specutils.io.registers import identify_spectrum_format

import jdaviz
#import jdaviz.core.data_identifiers as dataid
from jdaviz.core.config import list_configurations
from jdaviz.core.events import DataPromptMessage


default_file_to_config_mapping = {'JWST x1d': 'specviz', 'JWST s2d': 'imviz', 'JWST s3d': 'cubeviz',
                                  'MaNGA cube': 'cubeviz'}

formats_table = astropy.io.registry.get_formats(data_class=specutils.Spectrum1D, readwrite='Read')
spectral_formats = ['Spectrum1D', 'SpectrumList', 'SpectrumCollection', 'SpectralCube']
astropy.io.registry.get_formats(readwrite='Read')


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
        status = 'Error: Cannot determine format of the file to load.  Please specify a format'
    elif config not in valid_configs:
        status = f"Error: Config {config} not a valid configuration."
    elif current and config != current:
        status = 'Error: Mismatch between input file format and loaded configuration.'
    else:
        status = 'Success: Valid Format'

    return valid_format, config, status


def prompt_data(func):
    ''' Decorator to identity valid data format and prompt dialog '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        inst = args[0]
        filename = args[1]
        if isinstance(inst, jdaviz.core.helpers.ConfigHelper):
            app = inst.app
            current_config = inst._default_configuration
        else:
            app = inst
            current_config = app.get_configuration().get(
                'settings').get('configuration', 'default')

        valid_format, config, status = identify_data(filename, current=current_config)

        if 'success' in status.lower():
            return func(*args, **kwargs)

        msg = DataPromptMessage(status=status, data_format=valid_format, config=config,
                                current=current_config, sender=app)
        app.hub.broadcast(msg)
        #loaded = app.state.data_prompt.get('load', None)

        return func(*args, **kwargs)
        # if loaded:
        #     return func(*args, **kwargs)
        # else:
        #     print('cannot show data. exiting')
        #     #raise ValueError('cannot show data')
        #     return None

    return wrapper

