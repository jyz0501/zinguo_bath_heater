import aiohttp
import hashlib
import time
import json
import logging

_LOGGER = logging.getLogger(__name__)

class ZinguoAPI:
    def __init__(self, account, password):
        self.account = account
        self.password_hash = hashlib.sha1(password.encode()).hexdigest()
        self.token = None
        self.headers = {
            "User-Agent": "%E5%B3%A5%E6%9E%9C%E6%99%BA%E8%83%BD/2 CFNetwork/1327.0.4 Darwin/21.2.0",
            "Accept": "*/*",
            "Accept-Language": "zh-cn"
        }

    async def login(self):
        payload = {"account": self.account, "password": self.password_hash}
        headers = {**self.headers, "Content-Type": "text/plain;charset=UTF-8"}
        async with aiohttp.ClientSession() as session:
            async with session.post("https://iot.zinguo.com/api/v1/customer/login", data=json.dumps(payload), headers=headers) as resp:
                data = await resp.json(content_type=None)
                self.token = data.get("token")
                return self.token

    async def get_devices(self):
        if not self.token: await self.login()
        headers = {**self.headers, "x-access-token": str(self.token)}
        url = f"https://iot.zinguo.com/api/v1/customer/devices?tt={int(time.time()*1000)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                # 处理由于 mimetype 不标准导致的解析错误
                return await resp.json(content_type=None)

    async def send_control(self, payload):
        if not self.token: await self.login()
        headers = {**self.headers, "x-access-token": str(self.token), "Content-Type": "text/plain;charset=UTF-8"}
        # 默认结构补齐
        data = {
            "masterUser": self.account,
            "setParamter": False,
            "action": False,
            "warmingSwitch1": 0, "warmingSwitch2": 0, "lightSwitch": 0,
            "windSwitch": 0, "ventilationSwitch": 0, "turnOffAll": 0,
            **payload
        }
        async with aiohttp.ClientSession() as session:
            async with session.put("https://iot.zinguo.com/api/v1/wifiyuba/yuBaControl", data=json.dumps(data), headers=headers) as resp:
                return await resp.json(content_type=None)

    async def set_protection(self, mac, black_setting):
        if not self.token: await self.login()
        headers = {**self.headers, "x-access-token": str(self.token), "Content-Type": "text/plain;charset=UTF-8"}
        payload = {"mac": mac, "blackSetting": black_setting}
        async with aiohttp.ClientSession() as session:
            async with session.post("https://iot.zinguo.com/api/v1/wifiyuba/temperatureProtection", data=json.dumps(payload), headers=headers) as resp:
                return await resp.json(content_type=None)