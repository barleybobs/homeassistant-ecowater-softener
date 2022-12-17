"""Ecowater sensor platform."""
from datetime import datetime, timedelta
import logging
import re
from typing import Any, Callable, Dict, Optional

from ecowater_softener import Ecowater

from aiohttp import ClientError
from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_NAME,
    CONF_ACCESS_TOKEN,
    CONF_NAME,
    CONF_PATH,
    CONF_URL,
    UnitOfTime,
    UnitOfVolume,
    PERCENTAGE
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol

from .const import (
    ATTR_STATUS,
    ATTR_DAYS_UNTIL_OUT_OF_SALT,
    ATTR_OUT_OF_SALT_ON,
    ATTR_SALT_LEVEL_PERCENTAGE,
    ATTR_WATER_USAGE_TODAY,
    ATTR_WATER_USAGE_DAILY_AVERAGE,
    ATTR_WATER_AVAILABLE,
    ATTR_WATER_UNITS,
    ATTR_RECHARGE_ENABLED,
    ATTR_RECHARGE_SCHEDULED,
    ATTR_ALL_VALUES,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)
# Time between updating data from Ecowater
SCAN_INTERVAL = timedelta(minutes=30)

async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    # Update our config to include new repos and remove those that have been removed.
    if config_entry.options:
        config.update(config_entry.options)
    session = async_get_clientsession(hass)
    username = config["username"]
    password = config["password"]
    serialnumber = config["serialnumber"]
    dateformat = config["dateformat"]
    sensors = [EcowaterSensor(username, password, serialnumber, dateformat)]
    async_add_entities(sensors, update_before_add=True)

class EcowaterSensor(Entity):
    """Representation of a Ecowater water softener sensor."""

    def __init__(self, username, password, serialnumber, dateformat):
        super().__init__()
        self._attrs: dict[str, Any] = {}
        self._icon = 'mdi:water'
        self._state = None
        self._available = True
        self._username = username
        self._password = password
        self._serialnumber = serialnumber
        self._dateformat = dateformat
        self._name = "Ecowater " + self._serialnumber

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def icon(self):
        """Return the icon of the entity."""
        return self._icon

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return "Ecowater-" + self._serialnumber

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self._attrs

    async def async_update(self):
        try:
            ecowaterDevice = Ecowater(self._username, self._password, self._serialnumber)
            data_json = await self.hass.async_add_executor_job(lambda: ecowaterDevice._get())

            nextRecharge_re = "device-info-nextRecharge'\)\.html\('(?P<nextRecharge>.*)'"

            self._attrs[ATTR_STATUS] = 'Online' if data_json['online'] == True else 'Offline'
            self._attrs[ATTR_DAYS_UNTIL_OUT_OF_SALT] = data_json['out_of_salt_days']

            # Checks if date is 'today' or 'tomorrow'
            if str(data_json['out_of_salt']).lower() == 'today':
                self._attrs[ATTR_OUT_OF_SALT_ON] = datetime.today().strftime('%Y-%m-%d')
            elif str(data_json['out_of_salt']).lower() == 'tomorrow':
                self._attrs[ATTR_OUT_OF_SALT_ON] = (datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            # Runs correct datetime.strptime() depending on date format entered during setup.
            elif self._dateformat == "dd/mm/yyyy":
                self._attrs[ATTR_OUT_OF_SALT_ON] = datetime.strptime(data_json['out_of_salt'], '%d/%m/%Y').strftime('%Y-%m-%d')
            elif self._dateformat == "mm/dd/yyyy":
                self._attrs[ATTR_OUT_OF_SALT_ON] = datetime.strptime(data_json['out_of_salt'], '%m/%d/%Y').strftime('%Y-%m-%d')
            else:
                self._attrs[ATTR_OUT_OF_SALT_ON] = ''
                _LOGGER.exception(
                    f"Error: Date format not set"
                )

            self._attrs[ATTR_SALT_LEVEL_PERCENTAGE] = data_json['salt_level_percent']
            self._attrs[ATTR_WATER_USAGE_TODAY] = data_json['water_today']
            self._attrs[ATTR_WATER_USAGE_DAILY_AVERAGE] = data_json['water_avg']
            self._attrs[ATTR_WATER_AVAILABLE] = data_json['water_avail']
            self._attrs[ATTR_WATER_UNITS] = str(data_json['water_units'])
            self._attrs[ATTR_RECHARGE_ENABLED] = data_json['rechargeEnabled']
            self._attrs[ATTR_RECHARGE_SCHEDULED] = False if ( re.search(nextRecharge_re, data_json['recharge']) ).group('nextRecharge') == 'Not Scheduled' else True
            self._attrs[ATTR_ALL_VALUES] = data_json
            self._state = 'Online' if data_json['online'] == True else 'Offline'
            self._available = True

        except Exception as e:
            self._available = False
            _LOGGER.exception(
                f"Error: {e}"
            )


class DaysUntilOutOfSaltSensor(EcowaterSensor):
    """Days Until Out of Salt Sensor (number of days)"""

    def __init__(self, username, password, serialnumber, dateformat):
        super().__init__(username, password, serialnumber, dateformat)
        self._name = "Days Until Out of Salt"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def state(self) -> Optional[str]:
        return self._attrs[ATTR_DAYS_UNTIL_OUT_OF_SALT]
     
    @property
    def unit_of_measurement(self) -> str:
        return UnitOfTime.DAYS
    
    @property
    def device_class(self) -> str:
        return "duration"

class OutOfSaltOnSensor(EcowaterSensor):
    """Out of Salt On Sensor (date)"""

    def __init__(self, username, password, serialnumber, dateformat):
        super().__init__(username, password, serialnumber, dateformat)
        self._name = "Out of Salt On"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def state(self) -> Optional[str]:
        # Source (self._attrs[ATTR_OUT_OF_SALT_ON]) is "%Y-%m-%d", so convert to ISO 8601
        return datetime.strptime(self._attrs[ATTR_OUT_OF_SALT_ON], '%Y-%m-%d').isoformat()

    @property
    def device_class(self) -> str:
        return "date"


class SaltLevelPercentageSensor(EcowaterSensor):
    """Salt Level Percentage Sensor (percentage)"""

    def __init__(self, username, password, serialnumber, dateformat):
        super().__init__(username, password, serialnumber, dateformat)
        self._name = "Salt Level Percentage"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def state(self) -> Optional[str]:
        return self._attrs[ATTR_SALT_LEVEL_PERCENTAGE]

    @property
    def unit_of_measurement(self) -> str:
        return PERCENTAGE


class WaterUsedTodaySensor(EcowaterSensor):
    """Water Used Today Sensor (number of units)"""

    def __init__(self, username, password, serialnumber, dateformat):
        super().__init__(username, password, serialnumber, dateformat)
        self._name = "Water Used Today"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def state(self) -> Optional[str]:
        return self._attrs[ATTR_WATER_USAGE_TODAY]

    @property
    def unit_of_measurement(self) -> str:
        if self._attrs[ATTR_WATER_UNITS] == 'Liters':
            return UnitOfVolume.LITERS
        
        elif self._attrs[ATTR_WATER_UNITS] == 'Gallons':
            return UnitOfVolume.GALLONS
        
        else:
            return "Unknown"
        
    @property
    def device_class(self) -> str:
        return "water"
    

class WaterUsedDayAverageSensor(EcowaterSensor):
    """Water Used by Day Average Sensor (number of units)"""

    def __init__(self, username, password, serialnumber, dateformat):
        super().__init__(username, password, serialnumber, dateformat)
        self._name = "Water Used by Day Average"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def state(self) -> Optional[str]:
        return self._attrs[ATTR_WATER_USAGE_DAILY_AVERAGE]

    @property
    def unit_of_measurement(self) -> str:
        if self._attrs[ATTR_WATER_UNITS] == 'Liters':
            return UnitOfVolume.LITERS
        
        elif self._attrs[ATTR_WATER_UNITS] == 'Gallons':
            return UnitOfVolume.GALLONS
        
        else:
            return "Unknown"
        
    @property
    def device_class(self) -> str:
        return "volume"


class WaterAvailableSensor(EcowaterSensor):
    """Water Available Sensor (number of units)"""

    def __init__(self, username, password, serialnumber, dateformat):
        super().__init__(username, password, serialnumber, dateformat)
        self._name = "Water Available"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def state(self) -> Optional[str]:
        return self._attrs[ATTR_WATER_AVAILABLE]

    @property
    def unit_of_measurement(self) -> str:
        if self._attrs[ATTR_WATER_UNITS] == 'Liters':
            return UnitOfVolume.LITERS
        
        elif self._attrs[ATTR_WATER_UNITS] == 'Gallons':
            return UnitOfVolume.GALLONS
        
        else:
            return "Unknown"
        
    @property
    def device_class(self) -> str:
        return "volume"