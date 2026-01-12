from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([ZinguoTemp(coordinator, mac) for mac in coordinator.data])

class ZinguoTemp(SensorEntity):
    def __init__(self, coordinator, mac):
        self.coordinator, self.mac = coordinator, mac
        self._attr_name = f"浴霸温度 ({mac[-4:]})"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_native_unit_of_measurement = "°C"
        self._attr_unique_id = f"zinguo_{mac}_temp"

    @property
    def native_value(self):
        return self.coordinator.data.get(self.mac, {}).get("temperature")

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.mac)}, "name": "峥果浴霸"}