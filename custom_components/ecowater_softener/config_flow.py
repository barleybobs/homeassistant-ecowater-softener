import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN

import ecowater_softener

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA_USER = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
        vol.Required("dateformat"): vol.In(['dd/mm/yyyy', 'mm/dd/yyyy'])  # Añadir opción de formato de fecha
    }
)

class EcowaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Ecowater config flow."""

    data: Optional[Dict[str, Any]]
    errors: Dict[str, str] = {}

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            self.data = user_input

            try:
                ecowater_account = await self.hass.async_add_executor_job(
                    lambda: ecowater_softener.EcowaterAccount(self.data["username"], self.data["password"])
                )
            except:
                errors["base"] = "login_fail"
                return self.async_show_form(
                    step_id="user",
                    data_schema=DATA_SCHEMA_USER,
                    errors=errors
                )

            ecowater_devices = await self.hass.async_add_executor_job(
                lambda: ecowater_account.get_devices()
            )

            existing_entries = self._async_current_entries()
            configured_serial_numbers = {entry.data["device_serial_number"] for entry in existing_entries}

            self.device_list = [device.serial_number for device in ecowater_devices if device.serial_number not in configured_serial_numbers]

            if len(self.device_list) == 0:
                return self.async_abort(reason="no_available_devices")

            return await self.async_step_device()

        return self.async_show_form(
            step_id="user", 
            data_schema=DATA_SCHEMA_USER
        )
    
    async def async_step_device(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked after a user has provided their Ecowater account credentials."""
        if user_input is not None:
            self.data["device_serial_number"] = user_input["device_serial_number"]

            # Crear entrada de configuración con el formato de fecha seleccionado
            return self.async_create_entry(
                title="Ecowater " + self.data["device_serial_number"], 
                data=self.data  # Aquí se almacena también el formato de fecha elegido
            )
        
        return self.async_show_form(
            step_id="device", data_schema=vol.Schema({
                vol.Required("device_serial_number"): vol.In(self.device_list)
            })
        )
