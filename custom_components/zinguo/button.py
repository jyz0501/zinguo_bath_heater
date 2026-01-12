"""Button platform for Zinguo."""
import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZinguoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Zinguo button platform."""
    coordinator: ZinguoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    device_info = coordinator.data

    entities = []
    entities.append(ZinguoTurnOffAllButton(coordinator, device_info))

    async_add_entities(entities)


class ZinguoTurnOffAllButton(CoordinatorEntity, ButtonEntity):
    """Representation of a Zinguo turn-off-all button."""

    def __init__(self, coordinator: ZinguoDataUpdateCoordinator, device_info: dict[str, Any]):
        """Initialize the button."""
        super().__init__(coordinator)
        self._device_info = device_info
        # 使用MAC地址作为唯一标识符，确保与其他实体保持一致
        device_id = coordinator.mac
        self._attr_unique_id = f"{device_id}_turn_off_all_button"
        self._attr_name = "全关"
        # 限制设备名称长度，避免实体名称过长
        device_name = coordinator.name[:32] if coordinator.name else "Zinguo"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": device_name,
            "manufacturer": "Zinguo",
            "model": device_info.get("deviceModel", "智能浴霸"),
            "sw_version": device_info.get("firmwareVersion", "Unknown Version"),
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        # 发送turnOffAll命令，值为1表示关闭所有开关
        await self.coordinator.send_control_command({"turnOffAll": 1})

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # 按钮实体不需要处理状态更新，直接通知HA
        self.async_write_ha_state()
