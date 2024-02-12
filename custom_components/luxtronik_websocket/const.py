"""Constants for the Luxtronik Websocket integration."""
from homeassistant.exceptions import HomeAssistantError

DOMAIN = "luxtronik_websocket"


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
