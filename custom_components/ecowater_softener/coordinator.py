from datetime import datetime, timedelta
import re
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from ecowater_softener import Ecowater

from .const import (
    STATUS,
    DAYS_UNTIL_OUT_OF_SALT,
    OUT_OF_SALT_ON,
    SALT_LEVEL_PERCENTAGE,
    WATER_USAGE_TODAY,
    WATER_USAGE_DAILY_AVERAGE,
    WATER_AVAILABLE,
    WATER_UNITS,
    RECHARGE_ENABLED,
    RECHARGE_SCHEDULED,
    LAST_UPDATE,
)

_LOGGER = logging.getLogger(__name__)

class EcowaterDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Ecowater data."""

    def __init__(self, hass, username, password, serialnumber, dateformat):
        """Initialize Ecowater coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Ecowater " + serialnumber,
            update_interval=timedelta(minutes=30),
        )
        self._username = username
        self._password = password
        self._serialnumber = serialnumber
        self._dateformat = dateformat
        self._last_update = None

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            data = {}

            ecowaterDevice = Ecowater(self._username, self._password, self._serialnumber)
            data_json = await self.hass.async_add_executor_job(lambda: ecowaterDevice._get())

            nextRecharge_re = r"device-info-nextRecharge'\)\.html\('(?P<nextRecharge>.*)'"

            data[STATUS] = 'Online' if data_json['online'] == True else 'Offline'
            data[DAYS_UNTIL_OUT_OF_SALT] = data_json['out_of_salt_days']

            # Checks if date is 'today' or 'tomorrow'
            if str(data_json['out_of_salt']).lower() == 'today':
                data[OUT_OF_SALT_ON] = datetime.today().strftime('%Y-%m-%d')
            elif str(data_json['out_of_salt']).lower() == 'tomorrow':
                data[OUT_OF_SALT_ON] = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
            elif str(data_json['out_of_salt']).lower() == 'yesterday':
                data[OUT_OF_SALT_ON] = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
            # Runs correct datetime.strptime() depending on date format entered during setup.
            elif self._dateformat == "dd/mm/yyyy":
                data[OUT_OF_SALT_ON] = datetime.strptime(data_json['out_of_salt'], '%d/%m/%Y').strftime('%d-%m-%Y')
            elif self._dateformat == "mm/dd/yyyy":
                data[OUT_OF_SALT_ON] = datetime.strptime(data_json['out_of_salt'], '%m/%d/%Y').strftime('%Y-%m-%d')
            else:
                data[OUT_OF_SALT_ON] = ''
                _LOGGER.exception(
                    f"Error: Date format not set"
                )

            data[SALT_LEVEL_PERCENTAGE] = data_json['salt_level_percent']
            data[WATER_USAGE_TODAY] = data_json['water_today']
            data[WATER_USAGE_DAILY_AVERAGE] = data_json['water_avg']
            data[WATER_AVAILABLE] = data_json['water_avail']
            data[WATER_UNITS] = str(data_json['water_units'])
            data[RECHARGE_ENABLED] = data_json['rechargeEnabled']
            data[RECHARGE_SCHEDULED] = False if ( re.search(nextRecharge_re, data_json['recharge']) ).group('nextRecharge') == 'Not Scheduled' else True
            
            # Update the last time when data is received from the API and the softener is 'Online', according to date format.
            if data[STATUS] == 'Online':
                now = datetime.now()
                if self._dateformat == "dd/mm/yyyy":
                    self._last_update = now.strftime('%d-%m-%Y - %H:%M')
                elif self._dateformat == "mm/dd/yyyy":
                    self._last_update = now.strftime('%m-%d-%Y - %H:%M')
                else:
                    self._last_update = now.strftime('%d-%m-%Y - %H:%M')
                    _LOGGER.exception(
                        f"Error: Date format not set for last update"
                    )

                data[LAST_UPDATE] = self._last_update
            else:
                if self._last_update:
                    data[LAST_UPDATE] = self._last_update
            
            return data
        except Exception as e:
            # Keeps the last updated date in case of error when downloading data
            if self._last_update:
                data[LAST_UPDATE] = self._last_update
            raise UpdateFailed(f"Error communicating with API: {e}")
