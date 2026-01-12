from homeassistant.components.select import SelectEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator, api = data["coordinator"], data["api"]
    entities = []
    for mac in coordinator.data:
        entities.append(ZinguoLinkSelect(coordinator, api, mac))
        entities.append(ZinguoMotoSelect(coordinator, api, mac))
    async_add_entities(entities)

class ZinguoLinkSelect(SelectEntity):
    _attr_options = ["不联动", "联动取暖1", "联动取暖1和2"]
    _map = {"不联动": 0, "联动取暖1": 1, "联动取暖1和2": 3}
    _inv = {0: "不联动", 1: "联动取暖1", 3: "联动取暖1和2"}

    def __init__(self, coordinator, api, mac):
        self.coordinator, self.api, self.mac = coordinator, api, mac
        self._attr_name = f"浴霸 联动模式 ({mac[-4:]})"
        self._attr_unique_id = f"zinguo_{mac}_linkage"

    @property
    def current_option(self):
        val = self.coordinator.data.get(self.mac, {}).get("comovement", 0)
        return self._inv.get(val, "不联动")

    async def async_select_option(self, option):
        await self.api.send_control({"mac": self.mac, "setParamter": True, "comovement": self._map[option]})
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.mac)}, "name": "峥果浴霸"}

class ZinguoMotoSelect(SelectEntity):
    _attr_options = ["单电机", "双电机"]

    def __init__(self, coordinator, api, mac):
        self.coordinator, self.api, self.mac = coordinator, api, mac
        self._attr_name = f"浴霸 电机模式 ({mac[-4:]})"
        self._attr_unique_id = f"zinguo_{mac}_moto_ver"

    @property
    def current_option(self):
        val = self.coordinator.data.get(self.mac, {}).get("motoVersion")
        return "单电机" if val == 1 else "双电机"

    async def async_select_option(self, option):
        val = 1 if option == "单电机" else 2
        await self.api.send_control({"mac": self.mac, "setParamter": True, "motoVersion": val})
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.mac)}, "name": "峥果浴霸"}