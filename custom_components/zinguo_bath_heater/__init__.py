import logging
from homeassistant.const import Platform
from .api import ZinguoAPI
from .coordinator import ZinguoCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# 定义所有需要加载的平台，注意增加了 Platform.TIME
PLATFORMS = [
    Platform.SWITCH, 
    Platform.SENSOR, 
    Platform.NUMBER, 
    Platform.SELECT, 
    Platform.TIME
]

async def async_setup_entry(hass, entry):
    """设置集成条目"""
    # 初始化 API
    api = ZinguoAPI(entry.data["account"], entry.data["password"])
    
    # 初始化协调器 (数据轮询器)
    polling_interval = entry.data.get("polling_interval", 30)
    coordinator = ZinguoCoordinator(hass, api, polling_interval)
    
    # 立即获取第一次数据
    await coordinator.async_config_entry_first_refresh()
    
    # 存储到全局变量
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "api": api
    }
    
    # 加载所有子平台
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass, entry):
    """卸载集成条目"""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok