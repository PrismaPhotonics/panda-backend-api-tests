"""Debug ConfigManager - check what's actually loaded."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager

# Test local environment
print("=" * 70)
print("Testing 'local' environment:")
print("=" * 70)
config_local = ConfigManager("local")
print(f"Current environment: {config_local.get_current_environment()}")
print(f"RabbitMQ config: {config_local.get('rabbitmq')}")
print()

# Test staging environment
print("=" * 70)
print("Testing 'staging' environment:")
print("=" * 70)
config_staging = ConfigManager("staging")
print(f"Current environment: {config_staging.get_current_environment()}")
print(f"RabbitMQ config: {config_staging.get('rabbitmq')}")

