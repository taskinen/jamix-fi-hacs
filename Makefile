.PHONY: start stop restart logs clean reset shell

# Start Home Assistant
start:
	@echo "Starting Home Assistant..."
	docker-compose up -d
	@echo "Home Assistant is starting. Access it at http://localhost:8123"
	@echo "Run 'make logs' to follow the startup logs"

# Stop Home Assistant
stop:
	@echo "Stopping Home Assistant..."
	docker-compose down

# Restart Home Assistant (useful after code changes)
restart:
	@echo "Restarting Home Assistant..."
	docker-compose restart homeassistant
	@echo "Restarted. Run 'make logs' to follow the logs"

# Follow logs
logs:
	docker-compose logs -f homeassistant

# Clean up (stop and remove containers)
clean:
	docker-compose down -v

# Reset everything (WARNING: deletes all configuration)
reset:
	@echo "WARNING: This will delete all Home Assistant configuration!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		rm -rf homeassistant/; \
		echo "Reset complete. Run 'make start' to begin fresh"; \
	else \
		echo "Cancelled"; \
	fi

# Open a shell in the container
shell:
	docker-compose exec homeassistant /bin/bash

# Check if integration files are mounted correctly
check:
	@echo "Checking mounted integration files..."
	@docker-compose exec homeassistant ls -la /config/custom_components/jamix_fi/ || echo "Container not running. Start it with 'make start'"

# Show help
help:
	@echo "Jamix FI Home Assistant Integration - Docker Testing"
	@echo ""
	@echo "Available commands:"
	@echo "  make start    - Start Home Assistant container"
	@echo "  make stop     - Stop Home Assistant container"
	@echo "  make restart  - Restart Home Assistant (use after code changes)"
	@echo "  make logs     - Follow Home Assistant logs"
	@echo "  make clean    - Stop and remove containers"
	@echo "  make reset    - Delete all configuration and start fresh"
	@echo "  make shell    - Open a shell in the container"
	@echo "  make check    - Verify integration files are mounted"
	@echo "  make help     - Show this help message"
	@echo ""
	@echo "First time setup:"
	@echo "  1. Run 'make start'"
	@echo "  2. Wait for startup (check with 'make logs')"
	@echo "  3. Open http://localhost:8123"
	@echo "  4. See TESTING.md for detailed instructions"
