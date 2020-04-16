"""This module contains code for the bias current monitor Bokeh plots.

Author
------

    - Matthew Bourque

Use
---

    This module can be used from the command line as such:

    ::

        from jwql.website.apps.jwql.monitor_pages import monitor_bias_bokeh
        monitor_template = monitor_bias_bokeh.BiasMonitor('NIRCam', 'NRCA3_FULL')
        script, div = monitor_template.embed("dark_current_time_figure")
"""

import datetime
import os

from astropy.io import fits
from astropy.time import Time
from bokeh.models.tickers import LogTicker
import numpy as np

from jwql.database.database_interface import session
from jwql.database.database_interface import NIRCamBiasStats
from jwql.database.database_interface import NIRCamDarkQueryHistory, NIRCamDarkPixelStats, NIRCamDarkDarkCurrent
from jwql.database.database_interface import NIRISSDarkQueryHistory, NIRISSDarkPixelStats, NIRISSDarkDarkCurrent
from jwql.database.database_interface import MIRIDarkQueryHistory, MIRIDarkPixelStats, MIRIDarkDarkCurrent
from jwql.database.database_interface import NIRSpecDarkQueryHistory, NIRSpecDarkPixelStats, NIRSpecDarkDarkCurrent
from jwql.database.database_interface import FGSDarkQueryHistory, FGSDarkPixelStats, FGSDarkDarkCurrent
from jwql.utils.constants import JWST_INSTRUMENT_NAMES_MIXEDCASE
from jwql.utils.utils import get_config
from jwql.bokeh_templating import BokehTemplate

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class BiasLevel(BokehTemplate):

    # Combine input parameters into a single property because we
    # do not want to invoke the setter unless both are updated
    @property
    def input_parameters(self):
        return (self.instrument, self.aperture, self.amp, self.mode)

    @input_parameters.setter
    def input_parameters(self, values):
        self.instrument, self.aperture, self.amp, self.mode = values
        self.pre_init()
        self.post_init()

    def _identify_tables(self):
        """Determine which database tables as associated with a given
        instrument"""

        mixed_case_name = JWST_INSTRUMENT_NAMES_MIXEDCASE[self.instrument.lower()]
        self.stats_table = eval('{}BiasStats'.format(mixed_case_name))

    def _load_data(self):
        """Query the database tables to get data"""

        # Determine which database tables are needed based on instrument
        self._identify_tables()

        # Query database for all data in bias stats with a matching aperture
        self.query_results = session.query(self.stats_table) \
            .filter(self.stats_table.aperture == self.aperture) \
            .all()

    def pre_init(self):

        # Start with default values for instrument and aperture because
        # BokehTemplate's __init__ method does not allow input arguments
        try:
            dummy_instrument = self.instrument
            dummy_aperture = self.aperture
            dummy_amp = self.amp
            dummy_mode = self.mode
            flag = True
        except AttributeError:
            self.instrument = 'foo'
            self.aperture = 'bar'
            self.amp = 'tar'
            self.mode = 'par'
            flag = False

        if flag:
            print('here')

            # dummy_instrument = self.instrument
            # dummy_aperture = self.aperture
            # dummy_amp = self.amp
            # dummy_mode = self.mode

            # self.instrument = 'NIRCam'
            # self.aperture = 'NRCA1_FULL'
            # self.amp = '1'
            # self.mode = 'even'

            # App design
            self.format_string = None
            self.interface_file = os.path.join(SCRIPT_DIR, 'yaml', 'bias_monitor_interface.yaml')

            # Gather data needed for plots
            print('Gathering data for {}/{}/{}'.format(self.aperture, self.amp, self.mode))
            self._load_data()
            signals_column = getattr(self.query_results[0], 'amp{}_{}_med'.format(self.amp, self.mode))
            self.timestamps, self.signals = [], []
            for result in self.query_results:
                time_datetime = datetime.datetime.strptime(result.expstart, '%Y-%m-%dT%H:%M:%S.%f')  # Convert to datetime
                time_mjd = Time(time_datetime, format='datetime', scale='utc')  # Convert to MJD
                self.timestamps.append(time_mjd.mjd)
                self.signals.append(getattr(result, 'amp{}_{}_med'.format(self.amp, self.mode)))

    def post_init(self):

        pass

# class BiasMonitor(BokehTemplate):

#     def pre_init(self):

#         self._instrument = 'NIRCam'

#         self.load_data()

#         # Zeroth group uncal signal plots
#         self.timestamps =
#         self.singals =


#     def post_init(self):

#         self._update_dark_v_time()
#         self._update_hist()
#         self._dark_mean_image()

#     def identify_tables(self):
#         """Determine which database tables as associated with a given
#         instrument"""

#         mixed_case_name = JWST_INSTRUMENT_NAMES_MIXEDCASE[self._instrument.lower()]
#         self.stats_table = eval('{}BiasStats'.format(mixed_case_name))

#     def load_data(self):
#         """Query the database tables to get data"""

#         # Determine which database tables are needed based on instrument
#         self.identify_tables()

#         # Query database for all data in NIRCamDarkDarkCurrent with a matching aperture
#         self.dark_table = session.query(self.stats_table) \
#             .filter(self.stats_table.aperture == self._aperture) \
#             .all()

#         self.pixel_table = session.query(self.pixel_table) \
#             .filter(self.pixel_table.detector == self.detector) \
#             .all()
