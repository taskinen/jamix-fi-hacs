"""Constants for the Jamix FI integration."""

DOMAIN = "jamix_fi"

# API endpoints
API_BASE_URL = "https://fi.jamix.cloud/apps/menuservice/rest/haku"
API_PUBLIC_ENDPOINT = f"{API_BASE_URL}/public"
API_MENU_ENDPOINT = f"{API_BASE_URL}/menu"

# Configuration keys
CONF_CUSTOMER_ID = "customer_id"
CONF_KITCHEN_ID = "kitchen_id"
CONF_KITCHEN_NAME = "kitchen_name"
CONF_CUSTOMER_NAME = "customer_name"

# Default values
DEFAULT_SCAN_INTERVAL = 3600  # 1 hour in seconds
DEFAULT_LANGUAGE = "fi"

# Attributes
ATTR_DATE = "date"
ATTR_WEEKDAY = "weekday"
ATTR_MEAL_OPTIONS = "meal_options"
ATTR_MENU_ITEMS = "menu_items"
ATTR_DIETS = "diets"
ATTR_INGREDIENTS = "ingredients"
ATTR_PORTION_SIZE = "portion_size"
