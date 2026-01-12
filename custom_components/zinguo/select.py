"""Select entities for Zinguo integration."""
import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ZinguoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zinguo select entities based on config entry."""
    coordinator: ZinguoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ZinguoLightAutoCloseSelect(coordinator)])

class ZinguoLightAutoCloseSelect(SelectEntity):
    """Representation of a Zinguo light auto close select entity."""

    def __init__(self, coordinator: ZinguoDataUpdateCoordinator) -> None:
        """Initialize the select entity."""
        self._coordinator = coordinator
        device_name = coordinator.name[:32] if coordinator.name else "Zinguo"
        self._attr_name = f"{device_name} Light Auto Close"
        self._attr_unique_id = f"{coordinator.mac}_light_auto_close"
        self._attr_icon = "mdi:clock-outline"
        # 添加设备信息，确保实体关联到正确的设备
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.mac)},
            "name": device_name,
            "manufacturer": "Zinguo",
            "model": coordinator.data.get("deviceModel", "智能浴霸") if coordinator.data else "智能浴霸",
            "sw_version": coordinator.data.get("firmwareVersion") if coordinator.data else None,
        }
        
        # Generate time options in 1-minute increments from 00:00 to 23:59
        self._attr_options = [
            f"{hour:02d}:{minute:02d}" 
            for hour in range(24) 
            for minute in range(60)
        ]

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        # Get lightAutoClose value from coordinator data
        light_auto_close = self._coordinator.data.get("lightAutoClose")
        if light_auto_close is None:
            return "00:00"
        
        # Handle both dict and int formats for lightAutoClose
        if isinstance(light_auto_close, dict):
            # If it's a dict, extract stopHour and stopMinute
            stop_hour = light_auto_close.get("stopHour", 0)
            stop_minute = light_auto_close.get("stopMinute", 0)
            return f"{stop_hour:02d}:{stop_minute:02d}"
        elif isinstance(light_auto_close, int):
            # If it's an int, treat as total minutes
            hours, minutes = divmod(light_auto_close, 60)
            return f"{hours:02d}:{minutes:02d}"
        else:
            # Unknown type, default to 00:00
            return "00:00"

    async def async_select_option(self, option: str) -> None:
        """Select an option."""
        # Parse the selected time
        hours, minutes = map(int, option.split(":"))
        
        # Get current lightAutoClose settings to preserve status
        current_light_auto_close = self._coordinator.data.get("lightAutoClose", {})
        
        # Determine current status
        if isinstance(current_light_auto_close, dict):
            status = current_light_auto_close.get("status", True)
        else:
            status = True  # Default to enabled if we don't know
        
        # Send command to device in the expected format (dictionary)
        await self._coordinator.send_control_command({
            "lightAutoClose": {
                "stopHour": hours,
                "stopMinute": minutes,
                "status": status
            }
        })

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(self._coordinator.async_add_listener(self.async_write_ha_state))

    async def async_update(self) -> None:
        """Update the entity."""
        await self._coordinator.async_request_refresh()
