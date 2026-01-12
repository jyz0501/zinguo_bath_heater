import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_POLLING_INTERVAL

class ZinguoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input["account"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("account"): str,
                vol.Required("password"): str,
                vol.Required("moto_version", default="2"): vol.In({"1": "单电机", "2": "双电机"}),
                vol.Optional(CONF_POLLING_INTERVAL, default=30): int,
            })
        )