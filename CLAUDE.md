# Jamix FI Home Assistant Integration

## API Documentation

### API Endpoints

**IMPORTANT:** Always use HTTPS URLs. HTTP URLs will redirect to HTTPS.

#### 1. Get Customers and Kitchens
```
GET https://fi.jamix.cloud/apps/menuservice/rest/haku/public
```
Returns a list of all customers with their associated kitchens.

#### 2. Get Menu Data
```
GET https://fi.jamix.cloud/apps/menuservice/rest/haku/menu/<customerID>/<kitchenID>
```

**GET Parameters:**
* `lang` - language (fi or en). Default: en
* `type` - response format (json or table). Default: json
* `date` - start date in format yyyymmdd. Default: 0 (disabled)
* `date2` - ending date in format yyyymmdd. Default: 0 (disabled)

### Example API Calls

**Get all customers:**
```bash
curl -s "https://fi.jamix.cloud/apps/menuservice/rest/haku/public" | python3 -m json.tool
```

**Get menu for customer 96574, kitchen 128:**
```bash
curl -s "https://fi.jamix.cloud/apps/menuservice/rest/haku/menu/96574/128?lang=fi&date=20251202&date2=20251208"
```

### API Response Structure

#### Public Endpoint Response
```json
[
  {
    "customerId": "96574",
    "kitchens": [
      {
        "kitchenName": "Pirkkalan Ruokapalvelut",
        "kitchenId": 128,
        "address": "",
        "city": "Pirkkala",
        "email": "",
        "phone": "",
        "info": "Muutokset mahdollisia!",
        "menuTypes": [
          {
            "menuTypeId": 2,
            "menuTypeName": "Koulut",
            "menus": [
              {
                "menuName": "Menu name",
                "menuAdditionalName": "Additional info",
                "menuId": 4322,
                "menuSettings": 6,
                "favorite": false
              }
            ]
          }
        ]
      }
    ]
  }
]
```

#### Menu Endpoint Response
```json
[
  {
    "kitchenName": "Pirkkalan Ruokapalvelut",
    "kitchenId": 128,
    "menuTypes": [
      {
        "menuTypeId": 2,
        "menuTypeName": "Koulut",
        "menus": [
          {
            "menuName": "Menu name",
            "menuId": 4322,
            "days": [
              {
                "date": 20251202,
                "weekday": 2,
                "mealoptions": [
                  {
                    "name": "Lounas",
                    "orderNumber": 5,
                    "id": 6,
                    "menuItems": [
                      {
                        "name": "Hernekeitto",
                        "orderNumber": 1000,
                        "portionSize": 200,
                        "diets": "M, L, G",
                        "ingredients": "ingredient list...",
                        "images": []
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
]
```

### Key Data Points

- **Weekday values**: 1 = Monday, 2 = Tuesday, ..., 7 = Sunday
- **Menu types**: "Koulut" (schools), "Päiväkodit" (daycare), etc.
- **Meal options**: "Aamupala" (breakfast), "Lounas" (lunch), "Välipala" (snack)
- **Diets**: M (milk-free), L (lactose-free), G (gluten-free)
- **Date format**: yyyymmdd (e.g., 20251202)

## Integration Structure

### Files Created

```
custom_components/jamix_fi/
├── __init__.py           # Integration setup
├── api.py               # API client for Jamix
├── brand/
│   ├── icon.png         # Integration icon
│   └── logo.png         # Integration logo
├── config_flow.py       # Configuration UI flow
├── const.py             # Constants
├── coordinator.py       # Data update coordinator
├── manifest.json        # Integration metadata
├── sensor.py            # Sensor entities
├── strings.json         # English translations
└── translations/
    ├── en.json          # English translations
    └── fi.json          # Finnish translations

.github/workflows/
├── ci.yml               # Syntax validation on push/PR
└── release.yml          # Manual release workflow

hacs.json                # HACS metadata
README.md               # Documentation
```

### Sensors Created

The integration creates 8 sensors per kitchen:
1. `sensor.[kitchen_name]_monday_menu`
2. `sensor.[kitchen_name]_tuesday_menu`
3. `sensor.[kitchen_name]_wednesday_menu`
4. `sensor.[kitchen_name]_thursday_menu`
5. `sensor.[kitchen_name]_friday_menu`
6. `sensor.[kitchen_name]_saturday_menu`
7. `sensor.[kitchen_name]_sunday_menu`
8. `sensor.[kitchen_name]_today_menu`

### Sensor Attributes

Each sensor includes:
- `menus`: List of menu data
  - `menu_type`: Type of menu (e.g., "Koulut")
  - `menu_name`: Name of the menu
  - `date`: Date in yyyymmdd format
  - `meal_options`: List of meal options
    - `name`: Meal name (e.g., "Lounas")
    - `menu_items`: List of food items
      - `name`: Item name
      - `portion_size`: Portion size in grams
      - `diets`: Dietary information
      - `ingredients`: Full ingredient list

## Testing

Example customer/kitchen combinations:
- Customer ID: 96574, Kitchen ID: 128 (Pirkkalan Ruokapalvelut)
- Customer ID: 96574, Kitchen ID: 115 (Kangasalan kaupunki)

## Releasing

- Releases are triggered manually via GitHub Actions (Actions → Release → Run workflow)
- Version can be specified manually or auto-incremented (minor version bump)
- The release workflow updates `manifest.json` version, creates a `vX.Y.Z` git tag, and creates a GitHub Release
- Release notes are auto-generated from commit history; internal commits (`ci:`, `docs:`, `chore:`, `style:`, `refactor:`, `test:`, `build:`) are excluded
- Use Conventional Commits style for commit messages (e.g., `feat:`, `fix:`, `chore:`)
- HACS discovers new versions via GitHub Releases

## Development Notes

- Data is refreshed every hour (3600 seconds)
- The integration fetches the current week's menu (Monday to Sunday)
- All API calls use async/await with 10-second timeout
- Config flow provides dropdown selection for both customers and kitchens
- CI runs Python syntax validation and JSON checks on every push/PR
