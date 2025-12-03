# Jamix FI - Home Assistant Integration

A Home Assistant integration that reads meal menus from the Jamix FI Cloud service.

## Description

This integration allows you to view weekly meal menus from Finnish schools, daycare centers, and other institutions that use the Jamix menu service. The integration fetches menu data from the Jamix FI Cloud API and provides it as Home Assistant sensors.

## Features

- Easy onboarding flow with customer and kitchen selection
- Automatic weekly menu updates (refreshed hourly)
- Sensors for each weekday showing the full menu
- Special "Today's Menu" sensor for quick access
- Detailed menu information including:
  - Meal options (breakfast, lunch, snacks)
  - Individual menu items
  - Dietary information (M, L, G, etc.)
  - Ingredients
  - Portion sizes

## Installation via HACS

1. Add this repository to HACS as a custom repository
2. Search for "Jamix FI" in HACS
3. Click "Download"
4. Restart Home Assistant

## Manual Installation

1. Copy the `custom_components/jamix_fi` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "+ ADD INTEGRATION"
3. Search for "Jamix FI"
4. Follow the configuration steps:
   - Select your customer from the list
   - Select your kitchen from the available kitchens
5. Click "Submit"

## Sensors

After configuration, the integration creates the following sensors:

- `sensor.[kitchen_name]_monday_menu` - Menu for Monday
- `sensor.[kitchen_name]_tuesday_menu` - Menu for Tuesday
- `sensor.[kitchen_name]_wednesday_menu` - Menu for Wednesday
- `sensor.[kitchen_name]_thursday_menu` - Menu for Thursday
- `sensor.[kitchen_name]_friday_menu` - Menu for Friday
- `sensor.[kitchen_name]_saturday_menu` - Menu for Saturday
- `sensor.[kitchen_name]_sunday_menu` - Menu for Sunday
- `sensor.[kitchen_name]_today_menu` - Today's menu

Each sensor includes detailed attributes with:
- Menu type (e.g., "Koulut", "Päiväkodit")
- Menu name
- Date
- Meal options with all menu items
- Dietary information and ingredients

## Example Usage

### Display Today's Menu in Lovelace

```yaml
type: markdown
content: |
  ## Today's Menu
  {% set menu = state_attr('sensor.pirkkalan_ruokapalvelut_today_menu', 'menus') %}
  {% if menu %}
    {% for m in menu %}
      ### {{ m.menu_type }}
      {% for meal in m.meal_options %}
        **{{ meal.name }}**
        {% for item in meal.menu_items %}
          - {{ item.name }} ({{ item.diets }})
        {% endfor %}
      {% endfor %}
    {% endfor %}
  {% else %}
    No menu available
  {% endif %}
```

## API Information

The integration uses the public Jamix FI Cloud API:
- Customer list: `https://fi.jamix.cloud/apps/menuservice/rest/haku/public`
- Menu data: `https://fi.jamix.cloud/apps/menuservice/rest/haku/menu/{customer_id}/{kitchen_id}`

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/taskinen/jamix-fi-hacs/issues).

## License

This project is licensed under the MIT License.
