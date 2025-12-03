"""Sensor platform for Jamix FI."""
import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_DATE,
    ATTR_DIETS,
    ATTR_INGREDIENTS,
    ATTR_MEAL_OPTIONS,
    ATTR_MENU_ITEMS,
    ATTR_PORTION_SIZE,
    ATTR_WEEKDAY,
    CONF_KITCHEN_NAME,
    DOMAIN,
)
from .coordinator import JamixDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

WEEKDAY_NAMES = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Jamix FI sensors from a config entry."""
    coordinator: JamixDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    kitchen_name = entry.data[CONF_KITCHEN_NAME]

    # Create sensors for each weekday (1-7)
    entities = []
    for weekday in range(1, 8):
        entities.append(
            JamixMenuSensor(
                coordinator,
                entry.entry_id,
                kitchen_name,
                weekday,
            )
        )

    # Also create a "today" sensor
    entities.append(
        JamixTodayMenuSensor(
            coordinator,
            entry.entry_id,
            kitchen_name,
        )
    )

    async_add_entities(entities)


class JamixMenuSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Jamix menu for a specific weekday."""

    def __init__(
        self,
        coordinator: JamixDataUpdateCoordinator,
        entry_id: str,
        kitchen_name: str,
        weekday: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._weekday = weekday
        self._kitchen_name = kitchen_name
        self._attr_name = f"{kitchen_name} {WEEKDAY_NAMES[weekday]} Menu"
        self._attr_unique_id = f"{entry_id}_{weekday}_menu"
        self._attr_icon = "mdi:silverware-fork-knife"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        menu_data = self._get_menu_for_weekday()
        if not menu_data:
            return "No menu available"

        # Return a summary of the menu
        meal_count = 0
        for menu in menu_data:
            day_info = menu.get("day_info", {})
            meal_options = day_info.get("meal_options", [])
            meal_count += len(meal_options)

        if meal_count == 0:
            return "No meals"

        return f"{meal_count} meal option(s)"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        menu_data = self._get_menu_for_weekday()
        if not menu_data:
            return {}

        attributes = {
            ATTR_WEEKDAY: self._weekday,
            "weekday_name": WEEKDAY_NAMES[self._weekday],
            "menus": [],
        }

        for menu in menu_data:
            menu_type = menu.get("menu_type", "")
            menu_name = menu.get("menu_name", "")
            day_info = menu.get("day_info", {})

            menu_attr = {
                "menu_type": menu_type,
                "menu_name": menu_name,
                ATTR_DATE: day_info.get("date"),
                ATTR_MEAL_OPTIONS: [],
            }

            for meal_option in day_info.get("meal_options", []):
                meal_attr = {
                    "name": meal_option.get("name"),
                    ATTR_MENU_ITEMS: [],
                }

                for item in meal_option.get("items", []):
                    item_attr = {
                        "name": item.get("name"),
                        ATTR_PORTION_SIZE: item.get("portion_size"),
                        ATTR_DIETS: item.get("diets"),
                        ATTR_INGREDIENTS: item.get("ingredients"),
                    }
                    meal_attr[ATTR_MENU_ITEMS].append(item_attr)

                menu_attr[ATTR_MEAL_OPTIONS].append(meal_attr)

            attributes["menus"].append(menu_attr)

        return attributes

    def _get_menu_for_weekday(self) -> list[dict[str, Any]]:
        """Get menu data for the specific weekday."""
        if not self.coordinator.data:
            return []

        days = self.coordinator.data.get("days", {})

        # Find the date that matches our weekday
        for date, menu_list in days.items():
            if menu_list and len(menu_list) > 0:
                day_info = menu_list[0].get("day_info", {})
                if day_info.get("weekday") == self._weekday:
                    return menu_list

        return []


class JamixTodayMenuSensor(CoordinatorEntity, SensorEntity):
    """Sensor for today's Jamix menu."""

    def __init__(
        self,
        coordinator: JamixDataUpdateCoordinator,
        entry_id: str,
        kitchen_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._kitchen_name = kitchen_name
        self._attr_name = f"{kitchen_name} Today's Menu"
        self._attr_unique_id = f"{entry_id}_today_menu"
        self._attr_icon = "mdi:food"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        menu_data = self._get_today_menu()
        if not menu_data:
            return "No menu available"

        # Return a summary of the menu
        meal_count = 0
        for menu in menu_data:
            day_info = menu.get("day_info", {})
            meal_options = day_info.get("meal_options", [])
            meal_count += len(meal_options)

        if meal_count == 0:
            return "No meals"

        return f"{meal_count} meal option(s)"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        menu_data = self._get_today_menu()
        if not menu_data:
            return {}

        today = datetime.now()
        attributes = {
            ATTR_WEEKDAY: today.isoweekday(),
            "weekday_name": WEEKDAY_NAMES[today.isoweekday()],
            "menus": [],
        }

        for menu in menu_data:
            menu_type = menu.get("menu_type", "")
            menu_name = menu.get("menu_name", "")
            day_info = menu.get("day_info", {})

            menu_attr = {
                "menu_type": menu_type,
                "menu_name": menu_name,
                ATTR_DATE: day_info.get("date"),
                ATTR_MEAL_OPTIONS: [],
            }

            for meal_option in day_info.get("meal_options", []):
                meal_attr = {
                    "name": meal_option.get("name"),
                    ATTR_MENU_ITEMS: [],
                }

                for item in meal_option.get("items", []):
                    item_attr = {
                        "name": item.get("name"),
                        ATTR_PORTION_SIZE: item.get("portion_size"),
                        ATTR_DIETS: item.get("diets"),
                        ATTR_INGREDIENTS: item.get("ingredients"),
                    }
                    meal_attr[ATTR_MENU_ITEMS].append(item_attr)

                menu_attr[ATTR_MEAL_OPTIONS].append(meal_attr)

            attributes["menus"].append(menu_attr)

        return attributes

    def _get_today_menu(self) -> list[dict[str, Any]]:
        """Get menu data for today."""
        if not self.coordinator.data:
            return []

        today = datetime.now()
        today_weekday = today.isoweekday()

        days = self.coordinator.data.get("days", {})

        # Find the date that matches today's weekday
        for date, menu_list in days.items():
            if menu_list and len(menu_list) > 0:
                day_info = menu_list[0].get("day_info", {})
                if day_info.get("weekday") == today_weekday:
                    return menu_list

        return []
