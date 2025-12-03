"""API client for Jamix FI."""
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp
import async_timeout

from .const import API_MENU_ENDPOINT, API_PUBLIC_ENDPOINT, DEFAULT_LANGUAGE

_LOGGER = logging.getLogger(__name__)


class JamixApiClient:
    """API client for Jamix FI."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._session = session

    async def get_customers(self) -> list[dict[str, Any]]:
        """Get list of all customers and their kitchens."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(API_PUBLIC_ENDPOINT)
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching customers: %s", err)
            raise
        except TimeoutError as err:
            _LOGGER.error("Timeout fetching customers: %s", err)
            raise

    async def get_menu(
        self,
        customer_id: str,
        kitchen_id: str,
        language: str = DEFAULT_LANGUAGE,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get menu data for a specific customer and kitchen."""
        # Default to current week if no dates provided
        if date_from is None:
            today = datetime.now()
            # Get Monday of current week
            monday = today - timedelta(days=today.weekday())
            date_from = monday.strftime("%Y%m%d")

        if date_to is None:
            today = datetime.now()
            # Get Sunday of current week
            sunday = today + timedelta(days=(6 - today.weekday()))
            date_to = sunday.strftime("%Y%m%d")

        url = f"{API_MENU_ENDPOINT}/{customer_id}/{kitchen_id}"
        params = {
            "lang": language,
            "date": date_from,
            "date2": date_to,
        }

        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(url, params=params)
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error(
                "Error fetching menu for customer %s, kitchen %s: %s",
                customer_id,
                kitchen_id,
                err,
            )
            raise
        except TimeoutError as err:
            _LOGGER.error(
                "Timeout fetching menu for customer %s, kitchen %s: %s",
                customer_id,
                kitchen_id,
                err,
            )
            raise

    def get_kitchen_by_id(
        self, customers: list[dict[str, Any]], customer_id: str, kitchen_id: str
    ) -> dict[str, Any] | None:
        """Find a specific kitchen by customer and kitchen ID."""
        for customer in customers:
            if customer.get("customerId") == customer_id:
                for kitchen in customer.get("kitchens", []):
                    if kitchen.get("kitchenId") == int(kitchen_id):
                        return kitchen
        return None
