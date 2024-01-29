import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA_USER = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
        vol.Required("serialnumber"): str,
        vol.Required("dateformat"): vol.In(['dd/mm/yyyy', 'mm/dd/yyyy']),
        vol.Required("usessalt", default=True, description='Uses Salt'): bool
    }
)

class EcowaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Ecowater config flow."""

    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            self.data = user_input
            return self.async_create_entry(title="Ecowater " + self.data["serialnumber"], data=self.data)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA_USER
        )
