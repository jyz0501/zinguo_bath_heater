import logging
import asyncio
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """设置平台实体"""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]
    
    entities = []
    if not coordinator.data:
        return

    for mac in coordinator.data:
        # 1. 基础功能开关
        switch_types = [
            ("照明", "lightSwitch", "mdi:lightbulb"),
            ("吹风", "windSwitch", "mdi:fan"),
            ("换气", "ventilationSwitch", "mdi:air-filter"),
            ("取暖1", "warmingSwitch1", "mdi:radiator"),
            ("取暖2", "warmingSwitch2", "mdi:radiator"),
        ]
        
        for name, key, icon in switch_types:
            entities.append(ZinguoLogicSwitch(coordinator, api, mac, name, key, icon))
        
        # 2. 特殊功能开关
        entities.append(ZinguoAllOffSwitch(coordinator, api, mac))
        entities.append(ZinguoProtectionSwitch(coordinator, api, mac))

    async_add_entities(entities)

class ZinguoLogicSwitch(CoordinatorEntity, SwitchEntity):
    """逻辑同步开关：处理取暖与吹风的图标联动"""
    def __init__(self, coordinator, api, mac, name, key, icon):
        super().__init__(coordinator)
        self.api, self.mac, self.key = api, mac, key
        self._attr_name = f"浴霸 {name} ({mac[-4:]})"
        self._attr_unique_id = f"zinguo_{mac}_{key}"
        self._attr_icon = icon

    @property
    def is_on(self):
        """1为开，2为关"""
        state = self.coordinator.data.get(self.mac, {}).get(self.key)
        return state == 1 or state == "1"

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_request_refresh()
        if not self.is_on:
            await self._execute_command(True)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_request_refresh()
        if self.is_on:
            await self._execute_command(False)

    async def _execute_command(self, target_on):
        payload = {
            "mac": self.mac,
            "warmingSwitch1": 0, "warmingSwitch2": 0, "lightSwitch": 0,
            "windSwitch": 0, "ventilationSwitch": 0, "turnOffAll": 0,
            "setParamter": False, "action": False,
            "masterUser": self.api.account
        }
        payload[self.key] = 1 # 触发翻转
        
        try:
            await self.api.send_control(payload)
            
            # --- 瞬间广播 UI 更新 ---
            new_all_data = dict(self.coordinator.data)
            device_data = dict(new_all_data[self.mac])
            device_data[self.key] = 1 if target_on else 2
            
            # 联动逻辑：开取暖 -> 必开吹风
            if target_on and self.key in ["warmingSwitch1", "warmingSwitch2"]:
                device_data["windSwitch"] = 1
            # 联动逻辑：关吹风 -> 必关取暖
            elif not target_on and self.key == "windSwitch":
                device_data["warmingSwitch1"] = 2
                device_data["warmingSwitch2"] = 2

            new_all_data[self.mac] = device_data
            self.coordinator.async_set_updated_data(new_all_data)
            
            # 延时确认刷新
            self.hass.loop.call_later(3, lambda: asyncio.create_task(self.coordinator.async_request_refresh()))
        except Exception as e:
            _LOGGER.error(f"操作失败: {e}")

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.mac)}, "name": "峥果浴霸"}

class ZinguoAllOffSwitch(CoordinatorEntity, SwitchEntity):
    """全关开关：瞬间关闭 HA 界面上所有图标"""
    def __init__(self, coordinator, api, mac):
        super().__init__(coordinator)
        self.api, self.mac = api, mac
        self._attr_name = f"浴霸 全关 ({mac[-4:]})"
        self._attr_unique_id = f"zinguo_{mac}_all_off"
        self._attr_icon = "mdi:power-off"

    @property
    def is_on(self):
        return False # 按钮平时显示为关闭状态

    async def async_turn_on(self, **kwargs):
        """按下全关按钮时"""
        payload = {
            "mac": self.mac, 
            "turnOffAll": 1, 
            "masterUser": self.api.account
        }
        
        try:
            # 1. 向物理设备发送全关指令
            await self.api.send_control(payload)
            
            # 2. --- 核心：瞬间同步 HA 界面 ---
            # 构造新的数据字典，将所有开关状态码强制设为 2 (关闭)
            new_all_data = dict(self.coordinator.data)
            device_data = dict(new_all_data[self.mac])
            
            _LOGGER.info(f"全关触发：瞬间同步 {self.mac} 所有开关图标为关闭状态")
            
            for key in ["lightSwitch", "windSwitch", "ventilationSwitch", "warmingSwitch1", "warmingSwitch2"]:
                device_data[key] = 2
            
            new_all_data[self.mac] = device_data
            
            # 3. 广播更新，所有图标会立即熄灭
            self.coordinator.async_set_updated_data(new_all_data)
            
            # 3秒后从云端拉取真实状态做最后对齐
            self.hass.loop.call_later(3, lambda: asyncio.create_task(self.coordinator.async_request_refresh()))
            
        except Exception as e:
            _LOGGER.error(f"全关操作失败: {e}")

    async def async_turn_off(self, **kwargs):
        pass

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.mac)}, "name": "峥果浴霸"}

class ZinguoProtectionSwitch(CoordinatorEntity, SwitchEntity):
    """温控保护开关"""
    def __init__(self, coordinator, api, mac):
        super().__init__(coordinator)
        self.api, self.mac = api, mac
        self._attr_name = f"浴霸 温控保护 ({mac[-4:]})"
        self._attr_unique_id = f"zinguo_{mac}_protection"
        self._attr_icon = "mdi:shield-check"

    @property
    def is_on(self):
        return self.coordinator.data.get(self.mac, {}).get("blackSetting", {}).get("status", False)

    async def _set_status(self, status):
        device = self.coordinator.data.get(self.mac, {})
        config = device.get("blackSetting", {"status": not status, "openTime": 5, "pauseTime": 5})
        config["status"] = status
        
        try:
            await self.api.set_protection(self.mac, config)
            # 同步更新 UI
            new_all_data = dict(self.coordinator.data)
            new_all_data[self.mac]["blackSetting"] = config
            self.coordinator.async_set_updated_data(new_all_data)
        except Exception as e:
            _LOGGER.error(f"温控保护设置失败: {e}")

    async def async_turn_on(self, **kwargs): await self._set_status(True)
    async def async_turn_off(self, **kwargs): await self._set_status(False)

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.mac)}, "name": "峥果浴霸"}