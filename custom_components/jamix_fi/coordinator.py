"""DataUpdateCoordinator for Jamix FI."""
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import JamixApiClient
from .const import DEFAULT_LANGUAGE, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class JamixDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Jamix data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: JamixApiClient,
        customer_id: str,
        kitchen_id: str,
    ) -> None:
        """Initialize the coordinator."""
        self.api = api
        self.customer_id = customer_id
        self.kitchen_id = kitchen_id

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            menu_data = await self.api.get_menu(
                self.customer_id,
                self.kitchen_id,
                language=DEFAULT_LANGUAGE,
            )

            # Process and structure the data
            processed_data = self._process_menu_data(menu_data)
            return processed_data

        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def _process_menu_data(self, menu_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Process raw menu data into a structured format."""
        if not menu_data:
            return {}

        # The API returns a list with one kitchen
        kitchen_data = menu_data[0] if menu_data else {}

        processed = {
            "kitchen_name": kitchen_data.get("kitchenName", ""),
            "kitchen_id": kitchen_data.get("kitchenId"),
            "info": kitchen_data.get("info", ""),
            "menu_types": [],
            "days": {},
        }

        # Process each menu type
        for menu_type in kitchen_data.get("menuTypes", []):
            menu_type_info = {
                "id": menu_type.get("menuTypeId"),
                "name": menu_type.get("menuTypeName"),
                "menus": [],
            }

            # Process each menu
            for menu in menu_type.get("menus", []):
                menu_info = {
                    "id": menu.get("menuId"),
                    "name": menu.get("menuName"),
                    "additional_name": menu.get("menuAdditionalName", ""),
                    "days": {},
                }

                # Process each day
                for day in menu.get("days", []):
                    date = str(day.get("date"))
                    day_info = {
                        "date": date,
                        "weekday": day.get("weekday"),
                        "meal_options": [],
                    }

                    # Process each meal option (breakfast, lunch, snack)
                    for meal_option in day.get("mealoptions", []):
                        meal_info = {
                            "name": meal_option.get("name"),
                            "id": meal_option.get("id"),
                            "order": meal_option.get("orderNumber"),
                            "items": [],
                        }

                        # Process each menu item
                        for item in meal_option.get("menuItems", []):
                            item_info = {
                                "name": item.get("name"),
                                "portion_size": item.get("portionSize"),
                                "diets": item.get("diets", ""),
                                "ingredients": item.get("ingredients", ""),
                                "order": item.get("orderNumber"),
                            }
                            meal_info["items"].append(item_info)

                        day_info["meal_options"].append(meal_info)

                    menu_info["days"][date] = day_info

                    # Also add to global days dict for easy access
                    if date not in processed["days"]:
                        processed["days"][date] = []
                    processed["days"][date].append(
                        {
                            "menu_type": menu_type_info["name"],
                            "menu_name": menu_info["name"],
                            "day_info": day_info,
                        }
                    )

                menu_type_info["menus"].append(menu_info)

            processed["menu_types"].append(menu_type_info)

        return processed
