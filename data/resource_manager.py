"""
Resource/Asset Manager for Super Mario Bros.

Provides:
- Efficient asset loading
- Asset caching and pooling
- Lazy loading support
- Asset reference counting
- Multiple format support
- Asset hot-reloading (dev)
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union

import pygame as pg


class AssetType(Enum):
    """Types of assets."""

    IMAGE = "image"
    SOUND = "sound"
    MUSIC = "music"
    FONT = "font"
    DATA = "data"


class AssetState(Enum):
    """Asset loading state."""

    PENDING = "pending"
    LOADING = "loading"
    LOADED = "loaded"
    FAILED = "failed"


@dataclass
class AssetInfo:
    """
    Asset metadata.

    Attributes:
        name: Asset name/ID
        asset_type: Type of asset
        file_path: Path to file
        state: Loading state
        data: Loaded asset data
        size_bytes: File size
        load_time_ms: Time to load
        ref_count: Reference count
        metadata: Additional metadata
    """

    name: str
    asset_type: AssetType
    file_path: str
    state: AssetState = AssetState.PENDING
    data: Any = None
    size_bytes: int = 0
    load_time_ms: float = 0.0
    ref_count: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class AssetConfig:
    """Configuration for asset manager."""

    # Cache settings
    max_cache_size_mb: int = 500
    # Auto-unload unused assets after (seconds)
    auto_unload_time: int = 300
    # Enable hot-reloading
    hot_reload: bool = False
    # Hot-reload check interval (seconds)
    hot_reload_interval: int = 5
    # Default image format
    default_image_format: str = "png"
    # Compress images on load
    compress_images: bool = False
    # Convert images to alpha
    alpha_convert: bool = True


class ResourceLoader:
    """
    Low-level resource loader.
    """

    @staticmethod
    def load_image(path: str, alpha_convert: bool = True, compress: bool = False) -> pg.Surface:
        """
        Load image from file.

        Args:
            path: File path
            alpha_convert: Convert to alpha surface
            compress: Compress image

        Returns:
            Loaded surface
        """
        try:
            surface = pg.image.load(path)

            if alpha_convert:
                try:
                    surface = surface.convert_alpha()
                except pg.error:
                    # no video mode available during headless testing
                    pass

            if compress:
                # Scale down for compression
                new_size = (surface.get_width() // 2, surface.get_height() // 2)
                surface = pg.transform.smoothscale(surface, new_size)

            return surface

        except pg.error as e:
            raise IOError(f"Failed to load image {path}: {e}")

    @staticmethod
    def load_sound(path: str) -> pg.mixer.Sound:
        """
        Load sound from file.

        Args:
            path: File path

        Returns:
            Loaded sound
        """
        try:
            return pg.mixer.Sound(path)
        except pg.error as e:
            raise IOError(f"Failed to load sound {path}: {e}")

    @staticmethod
    def load_music(path: str) -> str:
        """
        Load music file path (music is streamed).

        Args:
            path: File path

        Returns:
            File path
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Music file not found: {path}")
        return path

    @staticmethod
    def load_font(path: str, size: int) -> pg.font.Font:
        """
        Load font from file.

        Args:
            path: File path
            size: Font size

        Returns:
            Loaded font
        """
        try:
            return pg.font.Font(path, size)
        except pg.error as e:
            raise IOError(f"Failed to load font {path}: {e}")

    @staticmethod
    def load_data(path: str, format: str = "json") -> Any:
        """
        Load data file.

        Args:
            path: File path
            format: Data format (json, txt, etc.)

        Returns:
            Loaded data
        """
        import json

        try:
            with open(path, "r", encoding="utf-8") as f:
                if format == "json":
                    return json.load(f)
                else:
                    return f.read()
        except (IOError, json.JSONDecodeError) as e:
            raise IOError(f"Failed to load data {path}: {e}")


class AssetManager:
    """
    Central asset management system.

    Usage:
        assets = AssetManager()
        assets.load("mario", "graphics/mario.png", AssetType.IMAGE)
        mario_sprite = assets.get("mario")
    """

    def __init__(self, config: Optional[AssetConfig] = None) -> None:
        """
        Initialize asset manager.

        Args:
            config: Asset configuration
        """
        self.config = config or AssetConfig()

        # Asset storage
        self.assets: Dict[str, AssetInfo] = {}
        self._load_order: List[str] = []

        # Asset directories
        self.base_path = Path(".")
        self.directories: Dict[AssetType, Path] = {
            AssetType.IMAGE: Path("resources/graphics"),
            AssetType.SOUND: Path("resources/sound"),
            AssetType.MUSIC: Path("resources/music"),
            AssetType.FONT: Path("resources/fonts"),
            AssetType.DATA: Path("resources/data"),
        }

        # Statistics
        self._total_load_time = 0.0
        self._cache_size_bytes = 0

        # Hot-reload tracking
        self._file_times: Dict[str, float] = {}
        self._last_hot_reload_check = 0.0

        # Callbacks
        self._on_load_start: Optional[Callable[[str], None]] = None
        self._on_load_complete: Optional[Callable[[str], None]] = None
        self._on_load_error: Optional[Callable[[str, str], None]] = None

    def set_base_path(self, path: Union[str, Path]) -> None:
        """
        Set base path for assets.

        Args:
            path: Base directory path
        """
        self.base_path = Path(path)

    def set_directory(self, asset_type: AssetType, path: Union[str, Path]) -> None:
        """
        Set directory for asset type.

        Args:
            asset_type: Type of asset
            path: Directory path
        """
        self.directories[asset_type] = Path(path)

    def get_directory(self, asset_type: AssetType) -> Path:
        """Get directory for asset type."""
        return self.directories.get(asset_type, self.base_path)

    def load(self, name: str, file_path: str, asset_type: AssetType, **kwargs) -> AssetInfo:
        """
        Load asset.

        Args:
            name: Asset name/ID
            file_path: Relative file path
            asset_type: Type of asset
            **kwargs: Additional loading options

        Returns:
            Asset info
        """
        # Check if already loaded
        if name in self.assets:
            self.assets[name].ref_count += 1
            return self.assets[name]

        # Build full path
        dir_path = self.get_directory(asset_type)
        # build the directory path and allow fallback if the expected folder
        # doesn't exist (tests often create plain "graphics" instead of
        # "resources/graphics").
        full_dir = self.base_path / dir_path
        if not full_dir.exists():
            alt = self.base_path / dir_path.name
            if alt.exists():
                full_dir = alt
        full_path = full_dir / file_path

        # Create asset info
        info = AssetInfo(name=name, asset_type=asset_type, file_path=str(full_path))

        # Load asset
        start_time = __import__("time").time()

        try:
            info.state = AssetState.LOADING

            if self._on_load_start:
                self._on_load_start(name)

            # Load based on type
            if asset_type == AssetType.IMAGE:
                info.data = ResourceLoader.load_image(
                    str(full_path),
                    alpha_convert=kwargs.get("alpha_convert", self.config.alpha_convert),
                    compress=kwargs.get("compress", self.config.compress_images),
                )
            elif asset_type == AssetType.SOUND:
                info.data = ResourceLoader.load_sound(str(full_path))
            elif asset_type == AssetType.MUSIC:
                info.data = ResourceLoader.load_music(str(full_path))
            elif asset_type == AssetType.FONT:
                info.data = ResourceLoader.load_font(str(full_path), kwargs.get("size", 24))
            elif asset_type == AssetType.DATA:
                info.data = ResourceLoader.load_data(str(full_path), kwargs.get("format", "json"))

            info.state = AssetState.LOADED
            info.ref_count = 1

            # Get file size
            try:
                info.size_bytes = os.path.getsize(full_path)
                self._cache_size_bytes += info.size_bytes
            except OSError:
                pass

            if self._on_load_complete:
                self._on_load_complete(name)

        except Exception as e:
            info.state = AssetState.FAILED
            info.metadata["error"] = str(e)

            if self._on_load_error:
                self._on_load_error(name, str(e))

        finally:
            load_time = (__import__("time").time() - start_time) * 1000
            info.load_time_ms = load_time
            self._total_load_time += load_time

        # Store and track load order
        self.assets[name] = info
        self._load_order.append(name)

        # Track file time for hot-reload
        if self.config.hot_reload:
            try:
                self._file_times[name] = os.path.getmtime(full_path)
            except OSError:
                pass

        return info

    def load_batch(self, assets: List[tuple[str, str, AssetType]], **kwargs) -> Dict[str, AssetInfo]:
        """
        Load multiple assets.

        Args:
            assets: List of (name, file_path, asset_type) tuples
            **kwargs: Additional loading options

        Returns:
            Dictionary of loaded assets
        """
        results = {}

        for name, file_path, asset_type in assets:
            info = self.load(name, file_path, asset_type, **kwargs)
            results[name] = info

        return results

    def load_directory(self, asset_type: AssetType, pattern: str = "*", prefix: str = "") -> Dict[str, AssetInfo]:
        """
        Load all assets from directory.

        Args:
            asset_type: Type of assets
            pattern: File pattern (glob)
            prefix: Name prefix

        Returns:
            Dictionary of loaded assets
        """
        dir_path = self.get_directory(asset_type)
        full_path = self.base_path / dir_path

        if not full_path.exists():
            return {}

        results = {}

        for file_path in full_path.glob(pattern):
            if file_path.is_file():
                name = f"{prefix}{file_path.stem}"
                info = self.load(name, file_path.name, asset_type)
                results[name] = info

        return results

    def get(self, name: str) -> Any:
        """
        Get asset data.

        Args:
            name: Asset name

        Returns:
            Asset data or None
        """
        if name not in self.assets:
            return None

        info = self.assets[name]

        if info.state != AssetState.LOADED:
            return None

        info.ref_count += 1
        return info.data

    def get_or_load(self, name: str, file_path: str, asset_type: AssetType, **kwargs) -> Any:
        """
        Get asset or load if not loaded.

        Args:
            name: Asset name
            file_path: File path
            asset_type: Asset type
            **kwargs: Loading options

        Returns:
            Asset data
        """
        if name in self.assets:
            return self.get(name)

        info = self.load(name, file_path, asset_type, **kwargs)
        return info.data if info.state == AssetState.LOADED else None

    def unload(self, name: str, force: bool = False) -> bool:
        """
        Unload asset.

        Args:
            name: Asset name
            force: Force unload regardless of ref count

        Returns:
            True if unloaded
        """
        if name not in self.assets:
            return False

        info = self.assets[name]

        # Decrement ref count
        info.ref_count -= 1

        # Only unload when forced or count goes below zero.  A ref_count of zero
        # means the asset is unused but can stay cached for future requests.
        if force or info.ref_count < 0:
            # Free memory
            if info.data:
                if hasattr(info.data, "get_size"):
                    # Image
                    pass  # pygame handles cleanup
                elif hasattr(info.data, "get_length"):
                    # Sound
                    pass

            self._cache_size_bytes -= info.size_bytes

            del self.assets[name]

            if name in self._load_order:
                self._load_order.remove(name)

            return True

        return False

    def unload_unused(self, max_idle_time: int = None) -> int:
        """
        Unload unused assets.

        Args:
            max_idle_time: Max idle time in seconds

        Returns:
            Number of assets unloaded
        """
        count = 0

        for name in list(self.assets.keys()):
            info = self.assets[name]

            if info.ref_count <= 0:
                if self.unload(name):
                    count += 1

        return count

    def clear(self) -> None:
        """Clear all assets."""
        self.assets.clear()
        self._load_order.clear()
        self._cache_size_bytes = 0
        self._file_times.clear()

    def get_info(self, name: str) -> Optional[AssetInfo]:
        """Get asset info."""
        return self.assets.get(name)

    def get_stats(self) -> dict:
        """Get asset manager statistics."""
        loaded = sum(1 for a in self.assets.values() if a.state == AssetState.LOADED)
        failed = sum(1 for a in self.assets.values() if a.state == AssetState.FAILED)

        return {
            "total_assets": len(self.assets),
            "loaded": loaded,
            "failed": failed,
            "cache_size_mb": self._cache_size_bytes / (1024 * 1024),
            "max_cache_mb": self.config.max_cache_size_mb,
            "total_load_time_ms": self._total_load_time,
            "avg_load_time_ms": (self._total_load_time / len(self.assets) if self.assets else 0),
        }

    def check_hot_reload(self) -> List[str]:
        """
        Check for hot-reloaded assets.

        Returns:
            List of reloaded asset names
        """
        if not self.config.hot_reload:
            return []

        import time

        current_time = time.time()

        # Check interval
        if current_time - self._last_hot_reload_check < self.config.hot_reload_interval:
            return []

        self._last_hot_reload_check = current_time
        reloaded = []

        for name, info in self.assets.items():
            if info.state != AssetState.LOADED:
                continue

            try:
                current_mtime = os.path.getmtime(info.file_path)

                if current_mtime > self._file_times.get(name, 0):
                    # File changed, reload
                    old_ref_count = info.ref_count
                    self.unload(name, force=True)
                    self.load(
                        name,
                        info.file_path.replace(str(self.base_path / self.get_directory(info.asset_type)), "").lstrip(
                            "/"
                        ),
                        info.asset_type,
                    )
                    self.assets[name].ref_count = old_ref_count
                    reloaded.append(name)

            except (OSError, IOError):
                pass

        return reloaded

    def set_callbacks(
        self,
        on_load_start: Optional[Callable[[str], None]] = None,
        on_load_complete: Optional[Callable[[str], None]] = None,
        on_load_error: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        """Set loading callbacks."""
        self._on_load_start = on_load_start
        self._on_load_complete = on_load_complete
        self._on_load_error = on_load_error


class SpriteSheet:
    """
    Sprite sheet helper.
    """

    def __init__(self, image: pg.Surface, tile_size: tuple[int, int], margin: int = 0, spacing: int = 0) -> None:
        """
        Initialize sprite sheet.

        Args:
            image: Sprite sheet image
            tile_size: Size of each tile
            margin: Margin around sheet
            spacing: Spacing between tiles
        """
        self.image = image
        self.tile_size = tile_size
        self.margin = margin
        self.spacing = spacing

        self._cache: Dict[tuple[int, int], pg.Surface] = {}

    def get_sprite(self, x: int, y: int) -> pg.Surface:
        """
        Get sprite at position.

        Args:
            x: X tile position
            y: Y tile position

        Returns:
            Sprite surface
        """
        key = (x, y)

        if key not in self._cache:
            rect = self._calculate_rect(x, y)
            self._cache[key] = self.image.subsurface(rect)

        return self._cache[key]

    def _calculate_rect(self, x: int, y: int) -> pg.Rect:
        """Calculate sprite rectangle."""
        offset_x = self.margin + x * (self.tile_size[0] + self.spacing)
        offset_y = self.margin + y * (self.tile_size[1] + self.spacing)

        return pg.Rect(offset_x, offset_y, self.tile_size[0], self.tile_size[1])

    def get_sprites_in_row(self, row: int, count: int) -> List[pg.Surface]:
        """
        Get multiple sprites from row.

        Args:
            row: Row index
            count: Number of sprites

        Returns:
            List of sprite surfaces
        """
        return [self.get_sprite(x, row) for x in range(count)]

    def get_animation_frames(self, start_x: int, start_y: int, count: int, horizontal: bool = True) -> List[pg.Surface]:
        """
        Get animation frames.

        Args:
            start_x: Start X position
            start_y: Start Y position
            count: Number of frames
            horizontal: Horizontal or vertical strip

        Returns:
            List of frame surfaces
        """
        frames = []

        for i in range(count):
            if horizontal:
                frames.append(self.get_sprite(start_x + i, start_y))
            else:
                frames.append(self.get_sprite(start_x, start_y + i))

        return frames


# Preset configurations
PRESET_CONFIGS = {
    "development": AssetConfig(
        max_cache_size_mb=1000,
        auto_unload_time=60,
        hot_reload=True,
        hot_reload_interval=2,
        compress_images=False,
    ),
    "production": AssetConfig(
        max_cache_size_mb=500,
        auto_unload_time=300,
        hot_reload=False,
        compress_images=True,
        alpha_convert=True,
    ),
    "low_memory": AssetConfig(
        max_cache_size_mb=200,
        auto_unload_time=60,
        hot_reload=False,
        compress_images=True,
    ),
}


def create_asset_manager(preset: str = "production", base_path: Optional[Union[str, Path]] = None) -> AssetManager:
    """
    Create asset manager with preset config.

    Args:
        preset: Config preset name
        base_path: Base asset path

    Returns:
        Configured AssetManager
    """
    config = PRESET_CONFIGS.get(preset, AssetConfig())
    manager = AssetManager(config)

    if base_path:
        manager.set_base_path(base_path)

    return manager
