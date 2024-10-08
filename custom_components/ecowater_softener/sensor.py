from dataclasses import dataclass

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass
)
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import (
    UnitOfVolume,
    UnitOfVolumeFlowRate,
    UnitOfMass,
    UnitOfTime,
    PERCENTAGE
)

from .const import (
    DOMAIN,
    MODEL,
    SOFTWARE_VERSION,
    WATER_AVAILABLE,
    WATER_USAGE_TODAY,
    WATER_USAGE_DAILY_AVERAGE,
    CURRENT_WATER_FLOW,
    SALT_LEVEL_PERCENTAGE,
    OUT_OF_SALT_ON,
    DAYS_UNTIL_OUT_OF_SALT,
    SALT_TYPE,
    LAST_RECHARGE,
    DAYS_SINCE_RECHARGE,
    RECHARGE_ENABLED,
    RECHARGE_STATUS,
    ROCK_REMOVED,
    ROCK_REMOVED_DAILY_AVERAGE
)

from .coordinator import EcowaterDataCoordinator

@dataclass
class EcowaterSensorEntityDescription(SensorEntityDescription):
        """A class that describes sensor entities"""

SENSOR_TYPES: tuple[EcowaterSensorEntityDescription, ...] = (
    EcowaterSensorEntityDescription(
        key=WATER_AVAILABLE,
        name="Water Available",
        icon="mdi:water",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfVolume.GALLONS
    ),
    EcowaterSensorEntityDescription(
        key=WATER_USAGE_TODAY,
        name="Water Used Today",
        icon="mdi:water",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfVolume.GALLONS
    ),
    EcowaterSensorEntityDescription(
        key=WATER_USAGE_DAILY_AVERAGE,
        name="Average Water Used per Day",
        icon="mdi:water",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfVolume.GALLONS
    ),
    EcowaterSensorEntityDescription(
        key=CURRENT_WATER_FLOW,
        name="Water Flow",
        icon="mdi:water",
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfVolumeFlowRate.GALLONS_PER_MINUTE
    ),
    EcowaterSensorEntityDescription(
        key=SALT_LEVEL_PERCENTAGE,
        name="Salt Level Percentage",
        icon="mdi:altimeter",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE
    ),
    EcowaterSensorEntityDescription(
        key=OUT_OF_SALT_ON,
        name="Out of Salt Date",
        icon="mdi:calendar",
        device_class=SensorDeviceClass.DATE
    ),
    EcowaterSensorEntityDescription(
        key=DAYS_UNTIL_OUT_OF_SALT,
        name="Days Until Out of Salt",
        icon="mdi:calendar",
        native_unit_of_measurement=UnitOfTime.DAYS
    ),
    EcowaterSensorEntityDescription(
        key=SALT_TYPE,
        name="Salt Type",
        icon="mdi:shaker-outline"
    ),
    EcowaterSensorEntityDescription(
        key=LAST_RECHARGE,
        name="Last Recharge Date",
        icon="mdi:calendar",
        device_class=SensorDeviceClass.DATE
    ),
    EcowaterSensorEntityDescription(
        key=DAYS_SINCE_RECHARGE,
        name="Days Since Last Recharge",
        icon="mdi:calendar",
        native_unit_of_measurement=UnitOfTime.DAYS
    ),
    EcowaterSensorEntityDescription(
        key=RECHARGE_ENABLED,
        name="Recharge Enabled",
        icon="mdi:refresh"
    ),
    EcowaterSensorEntityDescription(
        key=RECHARGE_STATUS,
        name="Recharge Status",
        icon="mdi:refresh"
    ),
    EcowaterSensorEntityDescription(
        key=ROCK_REMOVED,
        name="Rock Removed",
        icon="mdi:grain",
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfMass.POUNDS
    ),
    EcowaterSensorEntityDescription(
        key=ROCK_REMOVED_DAILY_AVERAGE,
        name="Average Rock Removed per Day",
        icon="mdi:grain",
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfMass.POUNDS
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

    coordinator = EcowaterDataCoordinator(hass, config['username'], config['password'], config['device_serial_number']) 

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        EcowaterSensor(coordinator, description, config['device_serial_number'])
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
        serialnumber
    ) -> None:
        """Initialize the ecowater sensor."""
        super().__init__(coordinator)
        self.entity_description = description

        self._serialnumber = serialnumber

        self._attr_unique_id = "ecowater_" + serialnumber.lower() + "_" + self.entity_description.key
        self._attr_native_value = getattr(self.coordinator.data, self.entity_description.key)

    @property
    def native_unit_of_measurement(self) -> StateType:
        if self.entity_description.native_unit_of_measurement != None:
            return self.entity_description.native_unit_of_measurement

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = getattr(self.coordinator.data, self.entity_description.key)
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._serialnumber)},
            name="Ecowater " + self._serialnumber,
            manufacturer="Ecowater",
            serial_number=self._serialnumber,
            model = getattr(self.coordinator.data, MODEL),
            sw_version = getattr(self.coordinator.data, SOFTWARE_VERSION)
        )
