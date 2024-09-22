from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import (
    UnitOfVolume,
    UnitOfTime,
    PERCENTAGE,
)

from .const import (
    DOMAIN,
    STATUS,
    DAYS_UNTIL_OUT_OF_SALT,
    OUT_OF_SALT_ON,
    SALT_LEVEL_PERCENTAGE,
    WATER_USAGE_TODAY,
    WATER_USAGE_DAILY_AVERAGE,
    WATER_AVAILABLE,
    RECHARGE_ENABLED,
    RECHARGE_SCHEDULED,
    LAST_UPDATE,
)


from .coordinator import EcowaterDataCoordinator

@dataclass
class EcowaterSensorEntityDescription(SensorEntityDescription):
        """A class that describes sensor entities"""

SENSOR_TYPES: tuple[EcowaterSensorEntityDescription, ...] = (
    EcowaterSensorEntityDescription(
        key=STATUS,
        translation_key="status",
        icon="mdi:power",
    ),
    EcowaterSensorEntityDescription(
        key=WATER_AVAILABLE,
        translation_key="water_available",
        icon="mdi:water",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL,
    ),
    EcowaterSensorEntityDescription(
        key=WATER_USAGE_TODAY,
        translation_key="water_usage_today",
        icon="mdi:water",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    EcowaterSensorEntityDescription(
        key=WATER_USAGE_DAILY_AVERAGE,
        translation_key="water_usage_daily_average",
        icon="mdi:water",
    ),
    EcowaterSensorEntityDescription(
        key=SALT_LEVEL_PERCENTAGE,
        translation_key="salt_level_percentage",
        icon="mdi:altimeter",
        native_unit_of_measurement=PERCENTAGE,
    ),
    EcowaterSensorEntityDescription(
        key=OUT_OF_SALT_ON,
        translation_key="out_of_salt_on",
        icon="mdi:calendar",
    ),
    EcowaterSensorEntityDescription(
        key=DAYS_UNTIL_OUT_OF_SALT,
        translation_key="days_until_out_of_salt",
        icon="mdi:calendar",
        native_unit_of_measurement=UnitOfTime.DAYS,
    ),
    EcowaterSensorEntityDescription(
        key=RECHARGE_ENABLED,
        translation_key="recharge_enabled",
    ),
    EcowaterSensorEntityDescription(
        key=RECHARGE_SCHEDULED,
        translation_key="recharge_scheduled",
    ),
    EcowaterSensorEntityDescription(
        key=LAST_UPDATE,
        translation_key="last_update",
        icon="mdi:update",
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the ecowater sensor."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    if config_entry.options:
        config.update(config_entry.options)

    coordinator = EcowaterDataCoordinator(hass, config['username'], config['password'], config['serialnumber'], config['dateformat']) 

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        EcowaterSensor(coordinator, description, config['serialnumber'])
        for description in SENSOR_TYPES
    )

class EcowaterSensor(
    CoordinatorEntity[EcowaterDataCoordinator],
    SensorEntity,
):
    """Implementation of an ecowater sensor."""

    _attr_has_entity_name = True
    entity_description: EcowaterSensorEntityDescription

    def __init__(
        self,
        coordinator: EcowaterDataCoordinator,
        description: EcowaterSensorEntityDescription,
        serialnumber,
    ) -> None:
        """Initialize the ecowater sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = "ecowater_" + serialnumber.lower() + "_" + self.entity_description.key
        self._attr_native_value = coordinator.data[self.entity_description.key]
        self._serialnumber = serialnumber

    @property
    def native_unit_of_measurement(self) -> StateType:
        if self.entity_description.key.startswith('water'):
            if self.coordinator.data['water_units'].lower() == 'liters':
                return UnitOfVolume.LITERS
            elif self.coordinator.data['water_units'].lower() == 'gallons':
                return UnitOfVolume.GALLONS
        elif self.entity_description.native_unit_of_measurement != None:
            return self.entity_description.native_unit_of_measurement

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data[self.entity_description.key]
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._serialnumber)},
            name="Ecowater " + self._serialnumber,
            manufacturer="Ecowater",
        )
