"""Constants for Zinguo integration."""

DOMAIN = "zinguo"

# Configuration keys
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_MAC = "mac"
CONF_NAME = "name"

# API configuration - Multiple endpoints for fallback
API_ENDPOINTS = [
    "https://iot.zinguo.com/api/v1",
    "https://iot2.zinguo.com/api/v1"
]

# Default endpoint (will be updated by coordinator if another works better)
BASE_URL = API_ENDPOINTS[0]
LOGIN_URL = f"{BASE_URL}/customer/login"
DEVICES_URL = f"{BASE_URL}/customer/devices"
GET_DEVICE_URL = f"{BASE_URL}/device/getDeviceByMac"
CONTROL_URL = f"{BASE_URL}/wifiyuba/yuBaControl"

# Switch types
SWITCH_TYPES = {
    "light": {
        "name": "Light",
        "key": "lightSwitch",
        "icon": "mdi:lightbulb"
    },
    "ventilation": {
        "name": "Ventilation",
        "key": "ventilationSwitch",
        "icon": "mdi:air-filter"
    },
    "wind": {
        "name": "Wind",
        "key": "windSwitch",
        "icon": "mdi:fan"
    },
    "heater1": {
        "name": "Heater 1",
        "key": "warmingSwitch1",
        "icon": "mdi:radiator"
    },
    "heater2": {
        "name": "Heater 2",
        "key": "warmingSwitch2",
        "icon": "mdi:radiator"
    },
}

# Fan preset modes
PRESET_MODE_OFF = "off"
PRESET_MODE_COOL = "cool"
PRESET_MODE_HEAT_LOW = "heat_low"
PRESET_MODE_HEAT_HIGH = "heat_high"

PRESET_MODES = [
    PRESET_MODE_OFF,
    PRESET_MODE_COOL,
    PRESET_MODE_HEAT_LOW,
    PRESET_MODE_HEAT_HIGH
]
