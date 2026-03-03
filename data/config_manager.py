"""
Configuration manager for game settings.

Loads and manages configuration from YAML file.
Provides type-safe access to configuration values.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, TYPE_CHECKING

logger = logging.getLogger(__name__)

try:
    import yaml  # type: ignore[import-untyped]

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

if TYPE_CHECKING:
    pass

# Default configuration path
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "game.yaml")


@dataclass
class DisplayConfig:
    """Display configuration."""

    screen_width: int = 800
    screen_height: int = 600
    fps: int = 60
    fullscreen: bool = False
    vsync: bool = True
    show_fps: bool = False


@dataclass
class AudioConfig:
    """Audio configuration."""

    enabled: bool = True
    music_volume: float = 0.5
    sfx_volume: float = 0.7
    sound_quality: str = "high"


@dataclass
class GameplayConfig:
    """Gameplay configuration."""

    starting_lives: int = 3
    enable_auto_save: bool = True
    auto_save_interval: int = 300
    difficulty: str = "normal"
    level_time_limit: int = 400
    time_warning: int = 100
    score_multiplier: float = 1.0
    enable_combo_system: bool = True
    combo_decay_rate: float = 0.5


@dataclass
class ControlsConfig:
    """Controls configuration."""

    jump: str = "K_a"
    action: str = "K_s"
    left: str = "K_LEFT"
    right: str = "K_RIGHT"
    down: str = "K_DOWN"
    alt_jump: str = "K_SPACE"
    alt_action: str = "K_k"
    controller_enabled: bool = True
    controller_jump: int = 0
    controller_action: int = 1


@dataclass
class GraphicsConfig:
    """Graphics configuration."""

    enable_particles: bool = True
    max_particles: int = 1000
    enable_weather: bool = True
    enable_parallax: bool = True
    quality_preset: str = "high"
    texture_filtering: bool = True
    anti_aliasing: bool = False
    shadow_quality: str = "medium"


@dataclass
class PerformanceConfig:
    """Performance configuration."""

    enable_object_pooling: bool = True
    enemy_pool_size: int = 20
    particle_pool_size: int = 200
    fireball_pool_size: int = 10
    enable_async_loading: bool = True
    worker_threads: int = 2
    max_texture_memory: int = 256
    cache_sprites: bool = True


@dataclass
class DebugConfig:
    """Debug configuration."""

    enabled: bool = False
    show_hitboxes: bool = False
    show_fps_graph: bool = False
    god_mode: bool = False
    infinite_time: bool = False
    unlock_all_skins: bool = False
    skip_intro: bool = True


@dataclass
class SaveConfig:
    """Save system configuration."""

    max_save_slots: int = 3
    compression_enabled: bool = True
    backup_enabled: bool = True
    max_backups_per_slot: int = 3


@dataclass
class AchievementsConfig:
    """Achievements configuration."""

    enabled: bool = True
    show_notifications: bool = True
    sync_to_cloud: bool = False


@dataclass
class ChallengesConfig:
    """Challenges configuration."""

    enabled: bool = True
    daily_refresh_hour: int = 0
    weekly_refresh_day: str = "monday"


@dataclass
class NetworkConfig:
    """Network configuration."""

    enabled: bool = False
    leaderboard_url: str = ""
    sync_interval: int = 600


@dataclass
class Config:
    """Main configuration container."""

    display: DisplayConfig = field(default_factory=DisplayConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    gameplay: GameplayConfig = field(default_factory=GameplayConfig)
    controls: ControlsConfig = field(default_factory=ControlsConfig)
    graphics: GraphicsConfig = field(default_factory=GraphicsConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    debug: DebugConfig = field(default_factory=DebugConfig)
    save: SaveConfig = field(default_factory=SaveConfig)
    achievements: AchievementsConfig = field(default_factory=AchievementsConfig)
    challenges: ChallengesConfig = field(default_factory=ChallengesConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)


class ConfigManager:
    """
    Manager for game configuration.

    Loads configuration from YAML file and provides
    type-safe access to configuration values.

    Usage:
        config = ConfigManager()
        config.load()
        print(config.display.screen_width)
    """

    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize configuration manager.

        Args:
            config_path: Path to configuration file.
                        Uses default if not specified.
        """
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.config = Config()
        self._raw_config: Dict[str, Any] = {}
        self._is_loaded: bool = False

    def load(self) -> bool:
        """
        Load configuration from file.

        Returns:
            True if configuration loaded successfully,
            False if file not found or YAML unavailable.
        """
        if not YAML_AVAILABLE:
            logger.warning("PyYAML not installed. Using default configuration.")
            return False

        if not os.path.exists(self.config_path):
            logger.warning("Configuration file not found: %s. Using default configuration.", self.config_path)
            return False

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._raw_config = yaml.safe_load(f) or {}

            self._apply_config()
            self._is_loaded = True
            return True

        except yaml.YAMLError as e:
            logger.error("Error parsing configuration file: %s. Using default configuration.", e)
            return False

    def _apply_config(self) -> None:
        """Apply raw configuration to config object."""
        if "display" in self._raw_config:
            self._apply_section(self.config.display, self._raw_config["display"])

        if "audio" in self._raw_config:
            self._apply_section(self.config.audio, self._raw_config["audio"])

        if "gameplay" in self._raw_config:
            self._apply_section(self.config.gameplay, self._raw_config["gameplay"])

        if "controls" in self._raw_config:
            self._apply_section(self.config.controls, self._raw_config["controls"])

        if "graphics" in self._raw_config:
            self._apply_section(self.config.graphics, self._raw_config["graphics"])

        if "performance" in self._raw_config:
            self._apply_section(self.config.performance, self._raw_config["performance"])

        if "debug" in self._raw_config:
            self._apply_section(self.config.debug, self._raw_config["debug"])

        if "save" in self._raw_config:
            self._apply_section(self.config.save, self._raw_config["save"])

        if "achievements" in self._raw_config:
            self._apply_section(self.config.achievements, self._raw_config["achievements"])

        if "challenges" in self._raw_config:
            self._apply_section(self.config.challenges, self._raw_config["challenges"])

        if "network" in self._raw_config:
            self._apply_section(self.config.network, self._raw_config["network"])

    def _apply_section(self, config_obj: Any, data: Dict[str, Any]) -> None:
        """Apply configuration section to dataclass."""
        if not isinstance(data, dict):
            return

        for key, value in data.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)

    def save(self) -> bool:
        """
        Save current configuration to file.

        Returns:
            True if save successful, False otherwise.
        """
        if not YAML_AVAILABLE:
            return False

        try:
            # Ensure directory exists
            config_dir = os.path.dirname(self.config_path)
            os.makedirs(config_dir, exist_ok=True)

            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    self._raw_config,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                )
            return True

        except (IOError, OSError) as e:
            logger.error("Error saving configuration: %s", e)
            return False

    def reset_to_defaults(self) -> None:
        """Reset all configuration values to defaults."""
        self.config = Config()
        self._raw_config = {}
        self._is_loaded = False

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get configuration value by section and key.

        Args:
            section: Configuration section name
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        if section in self._raw_config:
            return self._raw_config[section].get(key, default)
        return default

    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            section: Configuration section name
            key: Configuration key
            value: Value to set
        """
        if section not in self._raw_config:
            self._raw_config[section] = {}
        self._raw_config[section][key] = value

        # Also update config object
        config_obj = getattr(self.config, section, None)
        if config_obj and hasattr(config_obj, key):
            setattr(config_obj, key, value)

    @property
    def is_loaded(self) -> bool:
        """Check if configuration is loaded."""
        return self._is_loaded


# Global configuration instance
_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global configuration manager instance."""
    global _config
    if _config is None:
        _config = ConfigManager()
        _config.load()
    return _config


def reload_config() -> ConfigManager:
    """Reload configuration from file."""
    global _config
    _config = ConfigManager()
    _config.load()
    return _config
