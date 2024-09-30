from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

import ecowater_softener

_LOGGER = logging.getLogger(__name__)

class EcowaterDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Ecowater data."""

    def __init__(self, hass, username, password, serialnumber):
        """Initialize Ecowater coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Ecowater " + serialnumber,
            update_interval=timedelta(minutes=10),
        )
        self._username = username
        self._password = password
        self._serialnumber = serialnumber

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:       
            ecowater_account = await self.hass.async_add_executor_job(lambda: ecowater_softener.EcowaterAccount(self._username, self._password))
            ecowater_devices = await self.hass.async_add_executor_job(lambda: ecowater_account.get_devices())
            device = list(filter(lambda device: device.serial_number == self._serialnumber ,ecowater_devices))[0]
            await self.hass.async_add_executor_job(lambda: device.update())

            return device
        except Exception as e:
            raise UpdateFailed(f"Error communicating with Ayla API: {e}")
