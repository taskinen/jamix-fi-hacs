# Testing the Jamix FI Integration with Docker

This guide explains how to test the Jamix FI Home Assistant integration locally using Docker Compose.

## Prerequisites

- Docker and Docker Compose installed on your system
- No other service running on port 8123 (or modify the port in docker-compose.yml)

## Quick Start

1. **Start the Home Assistant container:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for Home Assistant to start** (usually takes 1-2 minutes on first run):
   ```bash
   docker-compose logs -f homeassistant
   ```
   Wait until you see: "Home Assistant initialized"

3. **Access Home Assistant:**
   Open your browser and navigate to: http://localhost:8123

4. **Complete the initial setup:**
   - Create your admin account
   - Set your location and time zone
   - Skip any integration suggestions (or configure them if desired)

## Adding the Jamix FI Integration

Once Home Assistant is running:

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Jamix FI"
4. Follow the configuration flow:
   - Select a customer (e.g., "96574 - Pirkkala")
   - Select a kitchen (e.g., "Pirkkalan Ruokapalvelut")
5. The integration will create 8 sensors for the selected kitchen

## Viewing the Sensors

After adding the integration:

1. Go to **Developer Tools** → **States**
2. Search for `jamix_fi` to see all sensors
3. Click on any sensor to view its attributes with menu data

Example sensors:
- `sensor.pirkkalan_ruokapalvelut_today_menu`
- `sensor.pirkkalan_ruokapalvelut_monday_menu`
- `sensor.pirkkalan_ruokapalvelut_tuesday_menu`
- etc.

## Viewing Logs

To see integration logs for debugging:

```bash
docker-compose logs -f homeassistant
```

Or from within Home Assistant:
- Go to **Settings** → **System** → **Logs**

## Stopping the Test Environment

```bash
docker-compose down
```

This stops and removes the container but keeps your configuration in the `homeassistant/` directory.

## Starting Fresh

If you want to completely reset Home Assistant:

```bash
docker-compose down
rm -rf homeassistant/
docker-compose up -d
```

## Updating Integration Code

The integration code is mounted as a read-only volume, so any changes you make to files in `custom_components/jamix_fi/` will be reflected after restarting Home Assistant:

```bash
docker-compose restart homeassistant
```

Or from within Home Assistant:
- Go to **Developer Tools** → **YAML** → **Restart**

## Troubleshooting

### Port 8123 already in use
If you have another service on port 8123, edit `docker-compose.yml` and change:
```yaml
ports:
  - "8124:8123"  # Use port 8124 instead
```

### Integration not showing up
1. Check logs: `docker-compose logs homeassistant`
2. Verify files are mounted: `docker-compose exec homeassistant ls -la /config/custom_components/jamix_fi/`
3. Restart the container: `docker-compose restart homeassistant`

### Permission issues
The `homeassistant/` directory needs to be writable by the container. If you encounter permission issues:
```bash
sudo chown -R 1000:1000 homeassistant/
```

## Test Customer/Kitchen Combinations

From the CLAUDE.md documentation:
- Customer ID: 96574, Kitchen ID: 128 (Pirkkalan Ruokapalvelut)
- Customer ID: 96574, Kitchen ID: 115 (Kangasalan kaupunki)

You can test with these or any other customer/kitchen from the public API endpoint.
