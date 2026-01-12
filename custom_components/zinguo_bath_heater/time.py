from homeassistant.components.time import TimeEntity
from datetime import time
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """设置时间平台"""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]
    
    entities = []
    for mac in coordinator.data:
        entities.append(ZinguoLightAutoCloseTime(coordinator, api, mac))
    
    async_add_entities(entities)

class ZinguoLightAutoCloseTime(TimeEntity):
    """照明小时与分钟合并后的时间选择实体"""
    
    def __init__(self, coordinator, api, mac):
        self.coordinator = coordinator
        self.api = api
        self.mac = mac
        self._attr_name = f"浴霸 照明自动关闭时间 ({mac[-4:]})"
        self._attr_unique_id = f"zinguo_{mac}_light_time_combined"
        self._attr_icon = "mdi:timer-cog"

    @property
    def native_value(self) -> time:
        """从 API 数据返回当前的 HH:MM"""
        device = self.coordinator.data.get(self.mac, {})
        # 获取嵌套字段 stopHour 和 stopMinute
        config = device.get("lightAutoClose", {})
        hr = config.get("stopHour", 0)
        mn = config.get("stopMinute", 0)
        # 确保数值合法
        return time(hour=max(0, min(23, hr)), minute=max(0, min(59, mn)))

    async def async_set_value(self, value: time) -> None:
        """用户在 HA 修改时间后，将 HH:MM 拆分发送"""
        payload = {
            "mac": self.mac,
            "setParamter": True,
            "lightAutoClose": {
                "status": True,
                "stopHour": value.hour,
                "stopMinute": value.minute
            }
        }
        await self.api.send_control(payload)
        # 发送后立即刷新本地状态
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        """关联到同一台浴霸设备"""
        return {
            "identifiers": {(DOMAIN, self.mac)},
            "name": "峥果浴霸",
            "manufacturer": "Zinguo"
        }