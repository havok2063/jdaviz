import numpy as np
import specutils
from astropy import units as u
from astropy.io import fits
from astropy.nddata import CCDData
from astropy.wcs import WCS
from astropy.utils import minversion
from traitlets import Bool, List, Unicode, observe
from specutils import manipulation, analysis, Spectrum1D

from jdaviz.core.custom_traitlets import IntHandleEmpty, FloatHandleEmpty
from jdaviz.core.events import SnackbarMessage, GlobalDisplayUnitChanged
from jdaviz.core.registries import tray_registry
from jdaviz.core.template_mixin import (PluginTemplateMixin,
                                        DatasetSelect, DatasetSelectMixin,
                                        FileImportSelectPluginComponent, HasFileImportSelect,
                                        SpectralSubsetSelectMixin,
                                        AddResultsMixin,
                                        SelectPluginComponent,
                                        SpectralContinuumMixin,
                                        skip_if_no_updates_since_last_active,
                                        with_spinner)
from jdaviz.core.unit_conversion_utils import convert_integrated_sb_unit
from jdaviz.core.user_api import PluginUserApi

__all__ = ['MapViz']


def check_unit(unit):
    if unit == 'degrees':
        unit = 'degree'
    elif 'ang' in unit:
        unit = unit.replace('ang', 'angstrom')
    return unit


@tray_registry('cubeviz-mapviz', label="MapViz", viewer_requirements=['image'])
class MapViz(PluginTemplateMixin, HasFileImportSelect, AddResultsMixin):
    """"""
    template_file = __file__, "mapviz.vue"
    uses_active_status = Bool(True).tag(sync=True)
    filename = Unicode().tag(sync=True)

    mapfile_items = List([]).tag(sync=True)
    mapfile_selected = Unicode("").tag(sync=True)
    map_selected = Unicode().tag(sync=True)

    available_maps = List([]).tag(sync=True)
    maps_obs_selected = Unicode().tag(sync=True)
    maps_obs_items = List().tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # description displayed under plugin title in tray
        self._plugin_description = 'Load 2d maps for a cube'

        self.add_results.viewer.filters = ['is_image_viewer']


        if not hasattr(self.app, '_mapfile'):
            self.map = FileImportSelectPluginComponent(self,
                                                        items='mapfile_items',
                                                        selected='mapfile_selected',
                                                        manual_options=['From File...'])
            # set the custom file parser for importing catalogs
            self.map._file_parser = self._file_parser
        else:
            self.mapfile_selected = self.app._mapfile
            self.map = type('MM', (), {'selected_obj': self._file_parser(self.app._mapfile)})()

    def vue_load_map(self, *args, **kwargs):
        print('mymap', self.map.selected_obj)
        self.wcs = self.map.selected_obj.pop('wcs')
        self.available_maps = list(self.map.selected_obj.keys())

    def vue_set_label(self, event):
        msg = SnackbarMessage(f"change event {event}", sender=self, color="success")
        self.hub.broadcast(msg)
        msg = SnackbarMessage(f"change map {self.map_selected}", sender=self, color="success")
        self.hub.broadcast(msg)
        self.results_label = self.map_selected
        #self.results_label_auto = self.map_selected

    def vue_add_map(self, *args):
        self.add_map(add_data=True)

    @with_spinner()
    def add_map(self, add_data=True):
        msg = SnackbarMessage("I am here", sender=self, color="success")
        self.hub.broadcast(msg)

        msg = SnackbarMessage("Now here", sender=self, color="success")
        self.hub.broadcast(msg)

        msg = SnackbarMessage(f"Using map {self.map_selected}", sender=self, color="success")
        self.hub.broadcast(msg)

        self.mapdata = self.map.selected_obj[self.map_selected]

        msg = SnackbarMessage(f"Have data {self.mapdata}", sender=self, color="success")
        self.hub.broadcast(msg)

        msg = SnackbarMessage(f"Have wcs {self.wcs}", sender=self, color="success")
        self.hub.broadcast(msg)

        if add_data:
            self.mapdata = CCDData(self.mapdata, wcs=self.wcs)
            self.add_results.add_results_from_plugin(self.mapdata, label=self.map_selected)

            msg = SnackbarMessage("{} added to data collection".format(self.results_label),
                                  sender=self, color="success")
            self.hub.broadcast(msg)

        return self.mapdata

    @staticmethod
    def _file_parser(path):
        mymaps = {}

        if not path:
            return '', {path: path}

        hack_ext = [1, 2, 3, 15, 30]
        with fits.open(path) as hdulist:
            for ext in hack_ext:

                # get and store the wcs info
                if ext == 2:
                    mymaps['wcs'] = WCS(hdulist[ext].header).celestial

                name = hdulist[ext].name.lower()
                hdr = hdulist[ext].header
                data = hdulist[ext].data
                ndim = hdulist[ext].data.ndim

                if ndim < 3:
                    nchan = None
                    label = f'{name}'.lower().replace('-', '_')
                    unit = hdr.get('BUNIT', '')
                    unit = check_unit(unit)
                    mymaps[label] = (data * u.Unit(unit)).T
                elif ndim == 3:
                    nchan, ny, nx = data.shape
                    for i in range(nchan):

                        if i + 1 < 10:
                            cname = f'C{i+1:02}' if 'C01' in hdr else f'C{i+1}'
                            uname = f'U{i+1:02}' if 'U01' in hdr else f'U{i+1}'
                        else:
                            cname = f'C{i+1}'
                            uname = f'U{i+1}'

                        unit = hdulist[ext].header.get(uname, '')
                        unit = check_unit(unit)

                        label = f'{name}_{hdr[f"{cname}"]}'.lower().replace('-', '_')
                        mymaps[label] = (data[i, :, :] * u.Unit(unit)).T

        return '', {path: mymaps}

