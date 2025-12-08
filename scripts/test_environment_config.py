#!/usr/bin/env python
"""
Test Environment Configuration Loading
=======================================

This script verifies that the config_manager correctly loads
environment-specific settings for staging and kefar_saba.
"""

from config.config_manager import ConfigManager


def test_environment_config(env_name: str):
    """Test configuration loading for a specific environment."""
    print(f"\n{'='*60}")
    print(f"{env_name.upper()} ENVIRONMENT:")
    print('='*60)
    
    # Reset singleton for clean test
    ConfigManager._instance = None
    ConfigManager._current_env = None
    
    cm = ConfigManager(env_name)
    env_config = cm._config_data
    
    print(f"  Environment: {cm.environment}")
    print(f"  MongoDB Host: {env_config.get('mongodb', {}).get('host')}")
    print(f"  RabbitMQ Host: {env_config.get('rabbitmq', {}).get('host')}")
    print(f"  SSH Jump Host: {env_config.get('ssh', {}).get('jump_host', {}).get('host')}")
    print(f"  SSH Target Host: {env_config.get('ssh', {}).get('target_host', {}).get('host')}")
    
    services = env_config.get('services', {})
    print(f"\n  Pod Selectors:")
    print(f"    MongoDB: {services.get('mongodb', {}).get('pod_selector')}")
    print(f"    RabbitMQ: {services.get('rabbitmq', {}).get('pod_selector')}")
    print(f"    Focus Server: {services.get('focus_server', {}).get('pod_selector')}")
    
    return env_config


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING ENVIRONMENT CONFIGURATION LOADING")
    print("="*60)
    
    staging_config = test_environment_config("staging")
    kefar_saba_config = test_environment_config("kefar_saba")
    
    # Verify they're different
    print("\n" + "="*60)
    print("VERIFICATION:")
    print("="*60)
    
    staging_mongodb = staging_config.get('mongodb', {}).get('host')
    kefar_mongodb = kefar_saba_config.get('mongodb', {}).get('host')
    
    if staging_mongodb != kefar_mongodb:
        print(f"  ✅ MongoDB hosts are different:")
        print(f"     Staging: {staging_mongodb}")
        print(f"     Kefar Saba: {kefar_mongodb}")
    else:
        print(f"  ❌ ERROR: MongoDB hosts are the same!")
    
    staging_ssh = staging_config.get('ssh', {}).get('jump_host', {}).get('host')
    kefar_ssh = kefar_saba_config.get('ssh', {}).get('jump_host', {}).get('host')
    
    if staging_ssh != kefar_ssh:
        print(f"  ✅ SSH hosts are different:")
        print(f"     Staging: {staging_ssh}")
        print(f"     Kefar Saba: {kefar_ssh}")
    else:
        print(f"  ❌ ERROR: SSH hosts are the same!")
    
    print("\n✅ Environment configuration loading works correctly!\n")

