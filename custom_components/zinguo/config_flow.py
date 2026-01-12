# config_flow.py
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import ConfigEntryNotReady
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_MAC, CONF_NAME # 导入常量
from .coordinator import ZinguoDataUpdateCoordinator # 导入协调器

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zinguo."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                # 使用协调器获取设备列表
                coordinator = ZinguoDataUpdateCoordinator(
                    self.hass,
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD]
                )
                # 获取设备列表
                try:
                    devices = await coordinator.async_get_devices()
                    _LOGGER.debug("Got devices: %s", devices)
                except Exception as ex:
                    _LOGGER.error("Failed to get devices: %s", ex, exc_info=True)
                    raise
                
                # 保存凭据以便后续步骤使用
                self._credentials = user_input
                
                # 如果只有一个设备，直接选择
                if len(devices) == 1:
                    device = devices[0]
                    return self.async_create_entry(
                        title=device.get("name", "Zinguo Device"),
                        data={
                            **user_input,
                            CONF_MAC: device.get("mac"),
                            CONF_NAME: device.get("name", "Zinguo Device")
                        }
                    )
                
                # 否则进入设备选择步骤
                self._devices = devices
                return await self.async_step_device()
            except Exception as ex: # 可以捕获更具体的异常
                _LOGGER.error("Config validation failed: %s", ex)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
    
    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle device selection step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            # 获取选中的设备
            device_id = user_input["device"]
            selected_device = next((d for d in self._devices if d["_id"] == device_id), None)
            
            if selected_device:
                return self.async_create_entry(
                    title=selected_device.get("name", "Zinguo Device"),
                    data={
                        **self._credentials,
                        CONF_MAC: selected_device.get("mac"),
                        CONF_NAME: selected_device.get("name", "Zinguo Device")
                    }
                )
            
            errors["base"] = "invalid_device"
        
        # 创建设备选择选项
        device_options = {}
        for device in self._devices:
            device_id = device["_id"]
            device_name = f"{device.get('name', 'Unknown')} ({device.get('mac', 'No MAC')})"
            device_options[device_id] = device_name
        
        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema(
                {
                    vol.Required("device"): vol.In(device_options),
                }
            ),
            errors=errors,
        )

    # 如果需要重新配置
    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle reconfiguration."""
        errors: dict[str, str] = {}
        # 获取当前条目的 ID，以便稍后更新
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])

        if user_input is not None:
            try:
                # --- 修改开始 ---
                # 使用协调器中的验证逻辑
                coordinator = ZinguoDataUpdateCoordinator(
                    self.hass,
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD]
                )
                # 验证凭据：尝试获取设备列表
                devices = await coordinator.async_get_devices()
                
                # 如果有设备，使用第一个设备的信息
                if devices:
                    title = devices[0].get("name", "Zinguo Device")
                    mac = devices[0].get("mac")
                    name = devices[0].get("name", "Zinguo Device")
                else:
                    title = "Zinguo Device"
                    # 保留原有设备的mac和name
                    mac = entry.data.get(CONF_MAC, "")
                    name = entry.data.get(CONF_NAME, "Zinguo Device")
                # --- 修改结束 ---

                # 更新现有条目，包含所有必要字段
                self.hass.config_entries.async_update_entry(
                    entry, 
                    data={
                        **user_input,
                        CONF_MAC: mac,
                        CONF_NAME: name
                    }, 
                    title=title
                )
                # 重新加载集成
                await self.hass.config_entries.async_reload(entry.entry_id)

                return self.async_abort(reason="reconfigure_successful")

            except Exception as ex:
                _LOGGER.error("Reconfig validation failed: %s", ex)
                errors["base"] = "cannot_connect"

        # 显示带有当前值的表单
        current_username = entry.data.get(CONF_USERNAME, "")
        current_password = entry.data.get(CONF_PASSWORD, "")

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default=current_username): str,
                    vol.Required(CONF_PASSWORD, default=current_password): str,
                }
            ),
            errors=errors,
        )
