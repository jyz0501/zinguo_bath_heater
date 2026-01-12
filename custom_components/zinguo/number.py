"""Number platform for Zinguo."""
import logging
from typing import Any, Optional

from homeassistant.components.number import NumberEntity, NumberDeviceClass, NumberMode
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
    """Set up Zinguo number entities based on a config entry."""
    coordinator: ZinguoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    device_info = coordinator.data

    entities = [
        ZinguoVentilationAutoCloseNumber(coordinator, device_info),
        ZinguoWarmingAutoCloseNumber(coordinator, device_info),
        ZinguoOverHeatAutoCloseNumber(coordinator, device_info),
    ]

    async_add_entities(entities, True)


class ZinguoNumberBase(CoordinatorEntity, NumberEntity):
    """Base class for Zinguo number entities."""

    def __init__(
        self,
        coordinator: ZinguoDataUpdateCoordinator,
        device_info: dict[str, Any],
        key: str,
        name_suffix: str,
        min_value: float,
        max_value: float,
        step: float,
        device_class: Optional[str] = None,
        unit_of_measurement: Optional[str] = None,
    ):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._device_info = device_info
        self._key = key
        # 使用MAC地址作为唯一标识符，确保与其他实体保持一致
        device_id = coordinator.mac
        device_name = coordinator.name[:32] if coordinator.name else "Zinguo"
        self._attr_name = f"{device_name} {name_suffix}"
        self._attr_unique_id = f"{device_id}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": device_name,
            "manufacturer": "Zinguo",
            "model": device_info.get("deviceModel", "智能浴霸"),
            "sw_version": device_info.get("firmwareVersion", "Unknown Version"),
        }
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        # Use slider mode for all number entities
        self._attr_mode = NumberMode.SLIDER
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit_of_measurement
        
        # Initialize state from coordinator's data if available
        if coordinator.data:
            self._attr_native_value = coordinator.data.get(key)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data.get(self._key)
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        # Send the control command to update the parameter
        await self.coordinator.send_control_command({self._key: int(value)})


class ZinguoVentilationAutoCloseNumber(ZinguoNumberBase):
    """Representation of a Zinguo ventilation auto close number entity."""

    def __init__(self, coordinator: ZinguoDataUpdateCoordinator, device_info: dict[str, Any]):
        """Initialize the ventilation auto close number entity."""
        super().__init__(
            coordinator=coordinator,
            device_info=device_info,
            key="ventilationAutoClose",
            name_suffix="换气自动关闭倒计时",
            min_value=0.0,
            max_value=60.0,
            step=1.0,
            unit_of_measurement="分钟",
        )


class ZinguoWarmingAutoCloseNumber(ZinguoNumberBase):
    """Representation of a Zinguo warming auto close number entity."""

    def __init__(self, coordinator: ZinguoDataUpdateCoordinator, device_info: dict[str, Any]):
        """Initialize the warming auto close number entity."""
        super().__init__(
            coordinator=coordinator,
            device_info=device_info,
            key="warmingAutoClose",
            name_suffix="取暖自动关闭倒计时",
            min_value=0.0,
            max_value=60.0,
            step=1.0,
            unit_of_measurement="分钟",
        )


class ZinguoOverHeatAutoCloseNumber(ZinguoNumberBase):
    """Representation of a Zinguo overheat auto close number entity."""

    def __init__(self, coordinator: ZinguoDataUpdateCoordinator, device_info: dict[str, Any]):
        """Initialize the overheat auto close number entity."""
        super().__init__(
            coordinator=coordinator,
            device_info=device_info,
            key="overHeatAutoClose",
            name_suffix="过热自动关闭温度",
            min_value=35.0,
            max_value=60.0,
            step=1.0,
            device_class=NumberDeviceClass.TEMPERATURE,
            unit_of_measurement="°C",
        )
