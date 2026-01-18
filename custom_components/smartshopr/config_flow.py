"""Config flow for SmartShopr integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SmartShoprApiClient, SmartShoprAuthError, SmartShoprApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
    }
)


class SmartShoprConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SmartShopr."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]

            # Validate the API key
            session = async_get_clientsession(self.hass)
            client = SmartShoprApiClient(api_key, session)

            try:
                if await client.validate_api_key():
                    # Check if already configured
                    await self.async_set_unique_id(api_key[:16])
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title="SmartShopr",
                        data={CONF_API_KEY: api_key},
                    )
                else:
                    errors["base"] = "invalid_auth"
            except SmartShoprAuthError:
                errors["base"] = "invalid_auth"
            except SmartShoprApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "api_key_url": "SmartShopr App → Settings → Home Assistant"
            },
        )


class SmartShoprOptionsFlow(config_entries.OptionsFlow):
    """Handle SmartShopr options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init")
