"""Config flow for Jamix FI integration."""
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import JamixApiClient
from .const import (
    CONF_CUSTOMER_ID,
    CONF_CUSTOMER_NAME,
    CONF_KITCHEN_ID,
    CONF_KITCHEN_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class JamixConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Jamix FI."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._customers: list[dict[str, Any]] = []
        self._selected_customer_id: str | None = None
        self._selected_customer_name: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - fetch and display customers."""
        errors = {}

        if user_input is None:
            # Fetch customers from API
            try:
                session = async_get_clientsession(self.hass)
                api = JamixApiClient(session)
                self._customers = await api.get_customers()

                if not self._customers:
                    errors["base"] = "no_customers"
                else:
                    # Create a dict of customer choices
                    customer_choices = {}
                    for customer in self._customers:
                        customer_id = customer.get("customerId")
                        # Try to find a meaningful name from kitchens
                        kitchens = customer.get("kitchens", [])
                        if kitchens:
                            # Use the city or name from first kitchen
                            first_kitchen = kitchens[0]
                            display_name = (
                                first_kitchen.get("city")
                                or first_kitchen.get("kitchenName")
                                or customer_id
                            )
                        else:
                            display_name = customer_id

                        customer_choices[customer_id] = f"{display_name} ({customer_id})"

                    return self.async_show_form(
                        step_id="user",
                        data_schema=vol.Schema(
                            {
                                vol.Required(CONF_CUSTOMER_ID): vol.In(customer_choices),
                            }
                        ),
                        errors=errors,
                    )

            except (aiohttp.ClientError, TimeoutError) as err:
                _LOGGER.error("Error fetching customers: %s", err)
                errors["base"] = "cannot_connect"
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema({}),
                    errors=errors,
                )
        else:
            # User selected a customer, move to kitchen selection
            self._selected_customer_id = user_input[CONF_CUSTOMER_ID]

            # Find customer name
            for customer in self._customers:
                if customer.get("customerId") == self._selected_customer_id:
                    kitchens = customer.get("kitchens", [])
                    if kitchens:
                        first_kitchen = kitchens[0]
                        self._selected_customer_name = (
                            first_kitchen.get("city")
                            or first_kitchen.get("kitchenName")
                            or self._selected_customer_id
                        )
                    break

            return await self.async_step_kitchen()

    async def async_step_kitchen(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle kitchen selection step."""
        errors = {}

        if user_input is None:
            # Find the selected customer's kitchens
            selected_customer = None
            for customer in self._customers:
                if customer.get("customerId") == self._selected_customer_id:
                    selected_customer = customer
                    break

            if not selected_customer:
                errors["base"] = "customer_not_found"
                return self.async_abort(reason="customer_not_found")

            kitchens = selected_customer.get("kitchens", [])
            if not kitchens:
                errors["base"] = "no_kitchens"
                return self.async_abort(reason="no_kitchens")

            # Create kitchen choices
            kitchen_choices = {}
            for kitchen in kitchens:
                kitchen_id = str(kitchen.get("kitchenId"))
                kitchen_name = kitchen.get("kitchenName", kitchen_id)
                city = kitchen.get("city", "")
                display = f"{kitchen_name}"
                if city:
                    display += f" - {city}"
                kitchen_choices[kitchen_id] = display

            return self.async_show_form(
                step_id="kitchen",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_KITCHEN_ID): vol.In(kitchen_choices),
                    }
                ),
                errors=errors,
            )
        else:
            # User selected a kitchen, create entry
            kitchen_id = user_input[CONF_KITCHEN_ID]

            # Find kitchen name
            kitchen_name = kitchen_id
            for customer in self._customers:
                if customer.get("customerId") == self._selected_customer_id:
                    for kitchen in customer.get("kitchens", []):
                        if str(kitchen.get("kitchenId")) == kitchen_id:
                            kitchen_name = kitchen.get("kitchenName", kitchen_id)
                            break
                    break

            # Check if already configured
            await self.async_set_unique_id(
                f"{self._selected_customer_id}_{kitchen_id}"
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"{kitchen_name}",
                data={
                    CONF_CUSTOMER_ID: self._selected_customer_id,
                    CONF_CUSTOMER_NAME: self._selected_customer_name,
                    CONF_KITCHEN_ID: kitchen_id,
                    CONF_KITCHEN_NAME: kitchen_name,
                },
            )
