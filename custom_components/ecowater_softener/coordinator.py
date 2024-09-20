from datetime import datetime, timedelta
import re
import logging
import asyncio

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import callback

from ecowater_softener import Ecowater

# Importamos las constantes desde const.py
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
    INPUT_NUMBER_UPDATE_INTERVAL  # Import the new constant
)

_LOGGER = logging.getLogger(__name__)

class EcowaterDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Ecowater data."""

    def __init__(self, hass, username, password, serialnumber, dateformat):
        """Initialize Ecowater coordinator."""
        self.hass = hass
        self._username = username
        self._password = password
        self._serialnumber = serialnumber
        self._dateformat = dateformat
        self._last_update = None

        # Set initial update interval
        update_interval = self._get_update_interval()
        super().__init__(
            hass,
            _LOGGER,
            name="Ecowater " + serialnumber,
            update_interval=update_interval
        )

        # Subscribe to changes in the button
        self.hass.bus.async_listen("state_changed", self._handle_button_press)

    def _get_update_interval(self):
        """Fetch the update interval from input_number entity."""
        try:
            # Aquí reemplazamos la referencia directa con la constante
            interval_minutes = self.hass.states.get(INPUT_NUMBER_UPDATE_INTERVAL).state
            return timedelta(minutes=int(float(interval_minutes)))
        except Exception as e:
            _LOGGER.error(f"Error fetching update interval: {e}")
            return timedelta(minutes=30)

    async def _async_update_data(self):
        """Fetch data from API and update the interval if necessary."""
        try:
            data = {}

            ecowaterDevice = Ecowater(self._username, self._password, self._serialnumber)
            data_json = await self.hass.async_add_executor_job(lambda: ecowaterDevice._get())

            nextRecharge_re = r"device-info-nextRecharge'\)\.html\('(?P<nextRecharge>.*)'"  # Regex to parse

            data[STATUS] = 'Online' if data_json['online'] else 'Offline'
            data[DAYS_UNTIL_OUT_OF_SALT] = data_json['out_of_salt_days']

            # Handling the salt out date logic
            data[OUT_OF_SALT_ON] = self._parse_salt_out_date(data_json['out_of_salt'])

            data[SALT_LEVEL_PERCENTAGE] = data_json['salt_level_percent']
            data[WATER_USAGE_TODAY] = data_json['water_today']
            data[WATER_USAGE_DAILY_AVERAGE] = data_json['water_avg']
            data[WATER_AVAILABLE] = data_json['water_avail']
            data[WATER_UNITS] = str(data_json['water_units'])
            data[RECHARGE_ENABLED] = data_json['rechargeEnabled']
            data[RECHARGE_SCHEDULED] = bool(re.search(nextRecharge_re, data_json['recharge']).group('nextRecharge') != 'Not Scheduled')
            
            # Update last update time
            now = datetime.now()
            self._last_update = self._format_last_update(now)
            data[LAST_UPDATE] = self._last_update

            return data
        except Exception as e:
            if self._last_update:
                data[LAST_UPDATE] = self._last_update
            raise UpdateFailed(f"Error communicating with API: {e}")

    @callback
    async def _handle_button_press(self, event):
        """Handle the button press to save the new update interval."""
        entity_id = event.data.get("entity_id")
        if entity_id == "input_button.ecowater_save_interval":
            _LOGGER.info("Button pressed to save update interval")

            # Fetch the new interval and update the coordinator's interval immediately
            new_interval = self._get_update_interval()
            self.update_interval = new_interval

            _LOGGER.info(f"Updated Ecowater update interval to {new_interval}")
    
    def _parse_salt_out_date(self, salt_out):
        """Parse the salt out date."""
        if salt_out.lower() == 'today':
            return datetime.today().strftime('%Y-%m-%d')
        elif salt_out.lower() == 'tomorrow':
            return (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        elif salt_out.lower() == 'yesterday':
            return (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        return ''

    def _format_last_update(self, now):
        """Format the last update time based on date format."""
        if self._dateformat == "dd/mm/yyyy":
            return now.strftime('%d-%m-%Y - %H:%M')
        elif self._dateformat == "mm/dd/yyyy":
            return now.strftime('%m-%d-%Y - %H:%M')
        return now.strftime('%d-%m-%Y - %H:%M')
