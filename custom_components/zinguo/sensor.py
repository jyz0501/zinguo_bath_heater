"""Platform for sensor integration."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ZinguoDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zinguo sensors based on a config entry."""
    coordinator: ZinguoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        TemperatureSensor(coordinator),
        OnlineStatusSensor(coordinator),
    ]

    async_add_entities(sensors, True)


class TemperatureSensor(SensorEntity):
    """Representation of a Zinguo temperature sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        self._coordinator = coordinator
        # 使用MAC地址作为设备唯一标识符，确保与其他实体保持一致
        device_id = coordinator.mac
        # 限制设备名称长度，避免实体名称过长
        device_name = coordinator.name[:32] if coordinator.name else "Zinguo"
        self._attr_name = f"{device_name} 温度"
        self._attr_unique_id = f"{device_id}_temperature"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": device_name,
            "manufacturer": "Zinguo",
            "model": coordinator.data.get("deviceModel", "Smart Bathroom Fan") if coordinator.data else "Smart Bathroom Fan",
            "sw_version": coordinator.data.get("firmwareVersion") if coordinator.data else None,
        }
        self._attr_native_unit_of_measurement = "°C"
        self._attr_device_class = "temperature"

    @property
    def native_value(self):
        """Return the temperature value."""
        if self._coordinator.data:
            temp = self._coordinator.data.get("temperature")
            if temp is not None:
                try:
                    return float(temp)
                except (ValueError, TypeError):
                    return None
        return None

    @property
    def available(self):
        """Return if entity is available."""
        # 传感器可用性不应仅依赖于数据是否存在，而应考虑设备是否在线
        return self._coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update the entity."""
        await self._coordinator.async_request_refresh()


class OnlineStatusSensor(SensorEntity):
    """Representation of a Zinguo online status sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        self._coordinator = coordinator
        # 使用MAC地址作为设备唯一标识符，确保与其他实体保持一致
        device_id = coordinator.mac
        # 限制设备名称长度，避免实体名称过长
        device_name = coordinator.name[:32] if coordinator.name else "Zinguo"
        self._attr_name = f"{device_name} 在线状态"
        self._attr_unique_id = f"{device_id}_online"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": device_name,
            "manufacturer": "Zinguo",
            "model": coordinator.data.get("deviceModel", "智能浴霸") if coordinator.data else "智能浴霸",
            "sw_version": coordinator.data.get("firmwareVersion") if coordinator.data else None,
        }
        self._attr_device_class = None

    @property
    def native_value(self):
        """Return the online status."""
        if self._coordinator.data:
            online = self._coordinator.data.get("online")
            return "在线" if online == 1 else "离线"
        return "Unknown"

    @property
    def available(self):
        """Return if entity is available."""
        # 传感器可用性不应仅依赖于数据是否存在，而应考虑设备是否在线
        return self._coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update the entity."""
        await self._coordinator.async_request_refresh()
