"""The Jamix FI integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import JamixApiClient
from .const import CONF_CUSTOMER_ID, CONF_KITCHEN_ID, DOMAIN
from .coordinator import JamixDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Jamix FI from a config entry."""
    customer_id = entry.data[CONF_CUSTOMER_ID]
    kitchen_id = entry.data[CONF_KITCHEN_ID]

    session = async_get_clientsession(hass)
    api = JamixApiClient(session)

    coordinator = JamixDataUpdateCoordinator(
        hass,
        api,
        customer_id,
        kitchen_id,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
