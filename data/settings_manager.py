"""Settings manager for persistent game settings."""

from __future__ import annotations

import json
import os
from typing import Any, Dict


class SettingsManager:
    """Manages game settings with persistence."""
    
    def __init__(self, settings_file: str = "game_settings.json") -> None:
        """Initialize settings manager.
        
        Args:
            settings_file: Path to settings file
        """
        self.settings_file = settings_file
        self.settings: Dict[str, Any] = self._load_default_settings()
        self.load()
    
    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default settings.
        
        Returns:
            Dictionary with default settings
        """
        return {
            "music_volume": 70,
            "sfx_volume": 80,
            "fullscreen": False,
            "show_fps": False,
            "last_level": "level1",
        }
    
    def load(self) -> None:
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to handle new settings
                    self.settings.update(loaded_settings)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Could not load settings: {e}")
            # Use defaults
    
    def save(self) -> None:
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Could not save settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
        self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings.
        
        Returns:
            Dictionary with all settings
        """
        return self.settings.copy()


# Global settings manager instance
_settings_manager: SettingsManager | None = None


def get_settings_manager() -> SettingsManager:
    """Get global settings manager instance.
    
    Returns:
        Settings manager instance
    """
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager
