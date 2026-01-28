import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open
import os

# Import the app creation function from our server
import sys
sys.path.append(str(Path(__file__).parent))

from server import create_app, load_settings


def test_load_settings_default():
    """Test loading default settings when settings.json doesn't exist."""
    # Temporarily rename settings.json if it exists
    settings_path = Path("settings.json")
    backup_path = Path("settings.json.bak")

    if settings_path.exists():
        settings_path.rename(backup_path)

    try:
        # Test default settings
        settings = load_settings()
        assert settings["port"] == 7000
    finally:
        # Restore the original file
        if backup_path.exists():
            backup_path.rename(settings_path)


def test_load_settings_custom():
    """Test loading custom settings from settings.json."""
    # Create a temporary settings file with custom values
    settings_path = Path("settings.json")
    backup_path = Path("settings.json.bak")

    # Backup existing settings file if it exists
    if settings_path.exists():
        settings_path.rename(backup_path)

    try:
        # Create a temporary settings file
        custom_settings = {"port": 8080}
        with open(settings_path, "w") as f:
            json.dump(custom_settings, f)

        # Test loading custom settings
        settings = load_settings()
        assert settings["port"] == 8080
    finally:
        # Clean up temporary file and restore backup
        if settings_path.exists():
            settings_path.unlink()
        if backup_path.exists():
            backup_path.rename(settings_path)


def test_app_creation():
    """Test that the app is created successfully."""
    # Temporarily rename settings.json if it exists to test defaults
    settings_path = Path("settings.json")
    backup_path = Path("settings.json.bak")

    if settings_path.exists():
        settings_path.rename(backup_path)

    try:
        app, settings = create_app()

        # Test that we get a valid app object
        assert app is not None
        assert hasattr(app, 'routes')

        # Test that we get valid settings
        assert 'port' in settings
    finally:
        # Restore the original file
        if backup_path.exists():
            backup_path.rename(settings_path)


if __name__ == "__main__":
    test_load_settings_default()
    test_load_settings_custom()
    test_app_creation()
    print("All tests passed!")