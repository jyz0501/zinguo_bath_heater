"""DataUpdateCoordinator for Zinguo integration."""
import logging
import json
from datetime import timedelta

import aiohttp
import async_timeout # Added missing import
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed # Added for better auth handling

from .const import (
    LOGIN_URL,
    DEVICES_URL,
    GET_DEVICE_URL,
    CONTROL_URL
)

_LOGGER = logging.getLogger(__name__)

class ZinguoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Zinguo data."""

    def __init__(self, hass, username, password, mac=None, name=None):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=name or "Zinguo",
            update_interval=timedelta(seconds=30), # Changed back from 300 to 30 for more frequent updates, adjust as needed
        )
        # Use 'username' to match CONF_USERNAME from const.py
        self.username = username
        self.password = password
        self.mac = mac
        self.token = None
        # API endpoint management
        self._base_url = None  # Will be set during login
        # 创建共享会话，禁用SSL验证以解决证书过期问题
        conn = aiohttp.TCPConnector(ssl=False)
        self._session = aiohttp.ClientSession(connector=conn)
        self.devices = [] # Store devices list for config flow

    async def _test_endpoint(self, base_url):
        """Test if a given API endpoint is working by attempting login."""
        import hashlib
        encrypted_password = hashlib.sha1(self.password.encode()).hexdigest()
        
        payload = {
            "account": self.username,
            "password": encrypted_password
        }

        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "User-Agent": "峥果智能/2 CFNetwork/3860.200.71 Darwin/25.1.0",
            "Accept": "*/*",
            "Accept-Language": "zh-cn",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

        login_url = f"{base_url}/customer/login"
        _LOGGER.debug("Testing endpoint: %s", base_url)
        
        try:
            async with self._session.post(login_url, json=payload, headers=headers) as response:
                response_text = await response.text()
                _LOGGER.debug("Endpoint %s response status: %d", base_url, response.status)
                
                if response.status == 200:
                    # Try to parse JSON to verify valid response
                    import json
                    data = json.loads(response_text)
                    if "token" in data:
                        _LOGGER.debug("Endpoint %s is working", base_url)
                        return True, data["token"]
                return False, None
        except Exception as ex:
            _LOGGER.debug("Endpoint %s test failed: %s", base_url, ex)
            return False, None

    async def _find_working_endpoint(self):
        """Find a working API endpoint from the list."""
        from .const import API_ENDPOINTS
        
        # Try each endpoint
        for endpoint in API_ENDPOINTS:
            is_working, token = await self._test_endpoint(endpoint)
            if is_working:
                _LOGGER.info("Found working endpoint: %s", endpoint)
                return endpoint, token
        
        _LOGGER.error("No working API endpoint found")
        raise Exception("No working API endpoint found")

    async def async_get_devices(self):
        """Get all devices for the user. Used in config flow."""
        try:
            async with async_timeout.timeout(30):
                # Login if needed
                if not self.token:
                    _LOGGER.debug("No token found, attempting login...")
                    await self._login()
                    _LOGGER.debug("Login successful, got token: %s", self.token[:10] + "..." if self.token else "None")

                # Use the detected base url or fallback to const BASE_URL
                from .const import DEVICES_URL as const_devices_url
                from .const import BASE_URL as const_base_url
                base_url = self._base_url if hasattr(self, '_base_url') and self._base_url else const_base_url
                devices_url = f"{base_url}/customer/devices"

                headers = {
                    "x-access-token": self.token,
                    "User-Agent": "峥果智能/2 CFNetwork/3860.200.71 Darwin/25.1.0",
                    "Accept": "*/*",
                    "Accept-Language": "zh-cn",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive"
                }
                
                _LOGGER.debug("Attempting to get devices from %s", devices_url)
                _LOGGER.debug("Devices request headers: %s", dict(headers))
                
                async with self._session.get(devices_url, headers=headers) as response:
                    _LOGGER.debug("Devices response status: %d", response.status)
                    _LOGGER.debug("Devices response headers: %s", dict(response.headers))
                    
                    response_text = await response.text()
                    _LOGGER.debug("Devices response text (first 500 chars): %s", response_text[:500])
                    
                    if response.status == 200:
                        # 手动解析JSON，忽略错误的Content-Type头
                        import json
                        try:
                            devices = json.loads(response_text)
                            self.devices = devices
                            _LOGGER.debug("Got devices: %s", devices)
                            return devices
                        except json.JSONDecodeError as ex:
                            # 真正的非JSON响应
                            _LOGGER.error("Devices API returned invalid JSON. Response (first 1000 chars): %s", response_text[:1000])
                            raise Exception(f"Devices API returned invalid JSON: {ex}")
                    else:
                        _LOGGER.error("Failed to get devices, status %d: %s", response.status, response_text)
                        raise Exception(f"Failed to get devices: Status {response.status}, Response: {response_text[:500]}")
        except Exception as err:
            _LOGGER.error("Error getting devices: %s", err, exc_info=True)
            raise

    async def _async_update_data(self):
        """Update data via API."""
        try:
            async with async_timeout.timeout(30):
                # Login if needed
                if not self.token:
                    _LOGGER.debug("No token found, attempting login...")
                    await self._login()
                    _LOGGER.debug("Login successful, token obtained.")

                # Get device status
                device_data = await self._get_device_status()
                # Process the raw data into a format suitable for entities
                processed_data = self._process_device_data(device_data)
                _LOGGER.debug("Successfully updated device data: %s", processed_data)
                return processed_data

        except ConfigEntryAuthFailed as err:
            # If authentication fails during an update, clear the token and re-raise
            _LOGGER.error("Authentication failed during update: %s", err)
            self.token = None
            raise
        except Exception as err:
            _LOGGER.error("Error updating Zinguo data: %s", err, exc_info=True)
            # Try to re-login on error, especially for 401 or token-related issues
            if isinstance(err, aiohttp.ClientResponseError) and err.status == 401:
                _LOGGER.debug("Got 401 during update, clearing token for re-login.")
                self.token = None
            # Don't raise ConfigEntryAuthFailed for non-auth errors, just UpdateFailed
            raise UpdateFailed(f"Error communicating with API: {err}")

    def _process_device_data(self, raw_data: dict) -> dict:
        """Process raw device data into a standardized format for entities."""
        # Define mapping for switch states based on actual device response
        # From test results, device uses:
        # 1: ON, 2: OFF
        status_map = {1: True, 2: False}
        
        # Device model mapping based on API response from /devicetype/listAll
        device_model_map = {
            "M1": "门窗报警器M2/M2S",
            "W1": "智能网关W1",
            "K2": "墙壁开关K2",
            "K2G": "开关群组K2G",
            "B2": "浴霸开关B2",
            "C2": "墙壁插座C2/C2S",
            "T2": "智能窗帘T2",
            "S2": "情景面板S2",
            "H2": "控制盒H2/H2S",
            "G6": "迎宾广告机G6"
        }
        
        # Get raw model code from device data
        raw_model = raw_data.get("model", "")
        # Map to human-readable name if available, otherwise use default
        device_model = device_model_map.get(raw_model, "智能浴霸")

        # Only extract and process the fields we actually need
        processed = {
            "id": raw_data.get("_id"),
            "mac": raw_data.get("mac"),
            "name": raw_data.get("name"),
            "online": raw_data.get("online"),
            "temperature": raw_data.get("temperature"),
            "lightSwitch": status_map.get(raw_data.get("lightSwitch"), False),
            "warmingSwitch1": status_map.get(raw_data.get("warmingSwitch1"), False),
            "warmingSwitch2": status_map.get(raw_data.get("warmingSwitch2"), False),
            "windSwitch": status_map.get(raw_data.get("windSwitch"), False),
            "ventilationSwitch": status_map.get(raw_data.get("ventilationSwitch"), False),
            "ventilationAutoClose": raw_data.get("ventilationAutoClose"),
            "overHeatAutoClose": raw_data.get("overHeatAutoClose"),
            "warmingAutoClose": raw_data.get("warmingAutoClose"),
            "lightAutoClose": raw_data.get("lightAutoClose"),
            "comovement": raw_data.get("comovement"),
            "hardwareVersion": raw_data.get("hardwareVersion"),
            "softwareVersion": raw_data.get("softwareVersion"),
            "deviceModel": device_model,
            "firmwareVersion": raw_data.get("softwareVersion", "Unknown")
        }
        _LOGGER.debug("Processed device data: %s", processed)
        return processed

    async def _login(self):
        """Login to Zinguo API using endpoint detection."""
        # 根据抓包数据，密码需要进行SHA-1加密
        import hashlib
        encrypted_password = hashlib.sha1(self.password.encode()).hexdigest()
        
        # Find a working endpoint first
        if not self._base_url:
            self._base_url, self.token = await self._find_working_endpoint()
            _LOGGER.debug("Login using detected endpoint: %s", self._base_url)
            return  # Token already obtained from _find_working_endpoint
        
        # If we already have a base_url, use it directly
        payload = {
            "account": self.username, # Use the corrected instance variable
            "password": encrypted_password
        }

        # 添加适当的请求头，模拟手机APP行为
        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "User-Agent": "峥果智能/2 CFNetwork/3860.200.71 Darwin/25.1.0",
            "Accept": "*/*",
            "Accept-Language": "zh-cn",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

        login_url = f"{self._base_url}/customer/login"
        _LOGGER.debug("Attempting login to %s with username: %s", login_url, self.username)
        _LOGGER.debug("Login payload: %s", payload)

        # Use the shared session
        async with self._session.post(login_url, json=payload, headers=headers) as response:
            _LOGGER.debug("Login response status: %d", response.status)
            _LOGGER.debug("Login response headers: %s", dict(response.headers))
            
            try:
                # 获取响应内容
                response_text = await response.text()
                _LOGGER.debug("Login response text (first 1000 chars): %s", response_text[:1000])
                
                if response.status == 200:
                    # 手动解析JSON，因为API返回的Content-Type可能不正确
                    data = json.loads(response_text)
                    
                    # 从响应中提取token
                    self.token = data.get("token")
                    if not self.token:
                        _LOGGER.error("Login failed: No token received in response: %s", data)
                        raise ConfigEntryAuthFailed("Login failed: No token received")
                    
                    _LOGGER.debug("Login successful for username: %s", self.username)
                    _LOGGER.debug("Got token: %s", self.token[:20] + "...")
                elif response.status == 401:
                     _LOGGER.error("Login failed: Invalid credentials for username: %s", self.username)
                     raise ConfigEntryAuthFailed("Invalid credentials")
                else:
                    _LOGGER.error("Login failed with status %d: %s", response.status, response_text)
                    raise ConfigEntryAuthFailed(f"Login failed with status {response.status}: {response_text}")
            except json.JSONDecodeError as ex:
                _LOGGER.error("Failed to parse login response as JSON: %s", ex)
                raise ConfigEntryAuthFailed(f"Login failed: Invalid response format: {ex}")
            except Exception as ex:
                _LOGGER.error("Exception during login: %s", ex)
                raise ConfigEntryAuthFailed(f"Login failed: {str(ex)}")

    async def _get_device_status(self):
        """Get device status from API."""
        if not self.token:
            raise UpdateFailed("Cannot fetch status: Not logged in")

        headers = {
            "x-access-token": self.token,
            "User-Agent": "峥果智能/2 CFNetwork/3860.200.71 Darwin/25.1.0",
            "Accept": "*/*",
            "Accept-Language": "zh-cn",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
        # 使用检测到的base_url或默认值
        base_url = self._base_url if hasattr(self, '_base_url') and self._base_url else getattr(self, 'base_url', GET_DEVICE_URL.rsplit('/', 1)[0])
        # 使用抓包数据中的正确端点，通过查询参数传递mac
        url = f"{base_url}/device/getDeviceByMac?mac={self.mac}"

        # Use the shared session
        async with self._session.get(url, headers=headers) as response:
            _LOGGER.debug("Device status response status: %d", response.status)
            _LOGGER.debug("Device status response headers: %s", dict(response.headers))
            
            response_text = await response.text()
            
            if response.status == 200:
                    # 手动解析JSON，因为API返回的Content-Type可能不正确
                    device = json.loads(response_text)
                    # 只记录必要的设备状态信息，避免日志过长
                    _LOGGER.debug("Fetched device status for MAC %s: online=%s, temp=%s, light=%s, warm1=%s, warm2=%s, wind=%s, vent=%s", 
                                 self.mac, device.get("online"), device.get("temperature"), 
                                 device.get("lightSwitch"), device.get("warmingSwitch1"), 
                                 device.get("warmingSwitch2"), device.get("windSwitch"), 
                                 device.get("ventilationSwitch"))
                    return device
            elif response.status == 401:
                # Token expired, re-login
                _LOGGER.warning("Token expired while fetching device status, attempting re-login.")
                self.token = None
                await self._login()
                return await self._get_device_status() # Retry after re-login
            else:
                _LOGGER.error("Failed to get device status for MAC %s, status %d: %s", self.mac, response.status, response_text)
                raise UpdateFailed(f"Failed to get device status: Status {response.status}, Response: {response_text}")

    async def send_control_command(self, payload):
        """Send control command to device with enhanced token management and retry logic."""
        max_retries = 2  # 最多重试2次
        retry_count = 0
        last_error = None
        
        while retry_count <= max_retries:
            try:
                if not self.token:
                    _LOGGER.debug("No token found, attempting login...")
                    await self._login()
                    _LOGGER.debug("Login successful, token obtained.")

                headers = {
                    "x-access-token": self.token,
                    "Content-Type": "application/json; charset=utf-8",
                    "User-Agent": "峥果智能/2 CFNetwork/3860.200.71 Darwin/25.1.0",
                    "Accept": "*/*",
                    "Accept-Language": "zh-cn",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive"
                }

                # Convert boolean values to device API format
                # According to _process_device_data, device uses: 1 = ON, 2 = OFF
                converted_payload = {}
                for key, value in payload.items():
                    # Convert boolean to device API format
                    if isinstance(value, bool):
                        converted_payload[key] = 1 if value else 2  # 1=ON, 2=OFF
                    else:
                        converted_payload[key] = value

                # Determine if this is a parameter setting command
                # Parameter keys based on the HAR log
                param_keys = ["ventilationAutoClose", "warmingAutoClose", "overHeatAutoClose", "lightAutoClose", "comovement", "motoVersion"]
                is_param_command = any(key in converted_payload for key in param_keys)

                # Get current device data if available
                current_data = self.data if hasattr(self, 'data') and self.data else {}
                
                # Build control payload based on command type
                control_payload = {
                    "mac": self.mac,
                    "masterUser": self.username,
                    "setParamter": is_param_command,
                    "action": False
                }
                
                if is_param_command:
                    # For parameter commands, include necessary param fields from current data or defaults
                    control_payload.update({
                        "comovement": current_data.get("comovement", 3),
                        "motoVersion": current_data.get("motoVersion", 2),
                        # Include the parameter being set
                        **converted_payload
                    })
                else:
                    # For switch commands, always use the latest local cached state as base
                    # This ensures we don't accidentally turn off other switches
                    
                    # Initialize with default values as fallback
                    current_status = {
                        "warmingSwitch1": 0,
                        "warmingSwitch2": 0,
                        "windSwitch": 0,
                        "lightSwitch": 0,
                        "ventilationSwitch": 0,
                        "turnOffAll": 0
                    }
                    
                    # Always use the latest cached data to maintain current state
                    # This is crucial to prevent unexpected switch behavior
                    if current_data:
                        # Convert boolean states to device API format (True -> 1, False -> 2)
                        # Important: Device expects 2 for OFF, not 0
                        current_status = {
                            "warmingSwitch1": 1 if current_data.get("warmingSwitch1") else 2,
                            "warmingSwitch2": 1 if current_data.get("warmingSwitch2") else 2,
                            "windSwitch": 1 if current_data.get("windSwitch") else 2,
                            "lightSwitch": 1 if current_data.get("lightSwitch") else 2,
                            "ventilationSwitch": 1 if current_data.get("ventilationSwitch") else 2,
                            "turnOffAll": 0
                        }
                    
                    # Apply only the specific changes requested by the user
                    # This ensures we don't modify any other switches unnecessarily
                    for key, value in converted_payload.items():
                        if key in current_status:
                            current_status[key] = value
                    
                    # Handle switch dependencies and comovement logic carefully
                    # Only affect the switches that are directly related
                    
                    # 1. If either warming switch is ON, ensure wind is also ON
                    #    But don't turn off wind if it was already on and warmings are being turned off
                    warming_1_on = current_status["warmingSwitch1"] == 1
                    warming_2_on = current_status["warmingSwitch2"] == 1
                    
                    if warming_1_on or warming_2_on:
                        # If any warming is on, wind must be on
                        current_status["windSwitch"] = 1
                    # Note: If both warmings are off, we leave wind as is - user can control it independently
                    
                    # 2. Light switch is completely independent - don't affect other switches
                    # 3. Ventilation switch is completely independent - don't affect other switches
                    
                    # Update the control payload with the final status
                    control_payload.update(current_status)

                _LOGGER.debug("Sending control command (attempt %d/%d): %s", retry_count + 1, max_retries + 1, control_payload)

                # 使用检测到的base_url或默认值
                base_url = self._base_url if hasattr(self, '_base_url') and self._base_url else getattr(self, 'base_url', CONTROL_URL.rsplit('/', 1)[0])
                control_url = f"{base_url}/wifiyuba/yuBaControl"
                
                # Use the shared session
                async with self._session.put(control_url, json=control_payload, headers=headers) as response:
                    _LOGGER.debug("Control command response status: %d", response.status)
                    _LOGGER.debug("Control command response headers: %s", dict(response.headers))
                    
                    response_text = await response.text()
                    _LOGGER.debug("Control command response text: %s", response_text)
                    
                    # 检查响应状态和内容
                    if response.status == 200:
                        _LOGGER.debug("Control command sent successfully.")
                        
                        # First, optimistically update the local state with the requested changes
                        # This provides immediate feedback to the user
                        optimistic_update = False
                        if self.data:
                            updated_data = self.data.copy()
                            for key, value in converted_payload.items():
                                if key in updated_data:
                                    updated_data[key] = value == 1
                                    optimistic_update = True
                            if optimistic_update:
                                self.data = updated_data
                                self.async_update_listeners()
                        
                        # Then, after a short delay, refresh from the actual device to ensure accuracy
                        # This handles the case where the device might take time to process the command
                        import asyncio
                        await asyncio.sleep(0.5)
                        
                        # Refresh data from device to get the actual state
                        actual_data = await self._async_update_data()
                        
                        # Only update and notify listeners if the actual state differs from our cached state
                        if actual_data != self.data:
                            self.data = actual_data
                            self.async_update_listeners()
                        
                        return True
                    
                    # 检查是否是令牌无效或过期
                    token_invalid = False
                    if response.status == 401:
                        token_invalid = True
                        _LOGGER.warning("Token expired (401), attempting re-login.")
                    elif "invalid_token" in response_text.lower():
                        token_invalid = True
                        _LOGGER.warning("Invalid token detected in response, attempting re-login.")
                    
                    if token_invalid:
                        # Token expired or invalid, re-login and retry
                        self.token = None
                        await self._login()
                        retry_count += 1
                        continue  # 重试发送命令
                    
                    # 其他错误状态
                    _LOGGER.error("Control command failed for MAC %s, status %d: %s", 
                                 self.mac, response.status, response_text)
                    return False
            
            except Exception as err:
                _LOGGER.error("Exception during send_control_command (attempt %d/%d): %s", 
                             retry_count + 1, max_retries + 1, err, exc_info=True)
                last_error = err
                
                # 检查是否是令牌相关错误
                if isinstance(err, aiohttp.ClientResponseError) and err.status == 401:
                    _LOGGER.warning("Got 401 error, attempting re-login...")
                    self.token = None
                    await self._login()
                    retry_count += 1
                    continue  # 重试发送命令
                elif "invalid_token" in str(err).lower():
                    _LOGGER.warning("Got invalid_token error, attempting re-login...")
                    self.token = None
                    await self._login()
                    retry_count += 1
                    continue  # 重试发送命令
                
                # 其他异常，不重试
                break
        
        # 重试次数耗尽
        _LOGGER.error("Control command failed after %d retries, last error: %s", 
                     max_retries + 1, last_error)
        return False

    async def async_shutdown(self):
        """Close the shared aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
        await super().async_shutdown()
