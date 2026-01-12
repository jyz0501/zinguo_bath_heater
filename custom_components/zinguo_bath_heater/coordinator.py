from datetime import timedelta
import logging
import async_timeout
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class ZinguoCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api, interval):
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name="Zinguo Device Data",
            update_interval=timedelta(seconds=interval)
        )

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                devices = await self.api.get_devices()
                if not isinstance(devices, list):
                    return {}
                return {dev["mac"]: dev for dev in devices}
        except Exception as err:
            raise UpdateFailed(f"无法同步峥果服务器数据: {err}")