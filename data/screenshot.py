"""
Screenshot System for Super Mario Bros.

Provides:
- Screenshot capture
- Auto-save on events
- Screenshot gallery
- EXIF metadata
- Batch export
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict

import pygame as pg


@dataclass
class ScreenshotInfo:
    """Screenshot metadata."""

    filename: str
    filepath: str
    timestamp: str
    width: int
    height: int
    game_state: dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


class ScreenshotManager:
    """
    Manager for capturing and organizing screenshots.

    Usage:
        ss_mgr = ScreenshotManager()
        ss_mgr.capture(screen, "level_complete")
        ss_mgr.save_gallery()
    """

    DEFAULT_DIR = "screenshots"
    SUPPORTED_FORMATS = ["png", "jpg", "bmp"]

    def __init__(self, save_dir: Optional[str] = None, auto_number: bool = True) -> None:
        """
        Initialize screenshot manager.

        Args:
            save_dir: Directory to save screenshots
            auto_number: Auto-number filenames
        """
        self.save_dir = Path(save_dir) if save_dir else Path(self.DEFAULT_DIR)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.auto_number = auto_number
        self.screenshot_count = 0
        self.screenshots: List[ScreenshotInfo] = []
        self.last_capture_time: float = 0

        # Settings
        self.format = "png"  # png, jpg, bmp
        self.quality = 95  # for jpg
        self.include_metadata = True
        self.max_screenshots = 1000

        # Cooldown (prevent spam)
        self.capture_cooldown = 500  # ms

        self._load_index()

    def _generate_filename(self, tag: str = "") -> str:
        """
        Generate unique filename.

        Args:
            tag: Optional tag for filename

        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if self.auto_number:
            self.screenshot_count += 1
            number = f"{self.screenshot_count:04d}"

            if tag:
                return f"{timestamp}_{tag}_{number}.{self.format}"
            return f"{timestamp}_{number}.{self.format}"

        if tag:
            return f"{timestamp}_{tag}.{self.format}"
        return f"{timestamp}.{self.format}"

    def capture(self, surface: pg.Surface, tag: str = "", metadata: Optional[dict] = None) -> Optional[ScreenshotInfo]:
        """
        Capture screenshot.

        Args:
            surface: Pygame surface to capture
            tag: Optional tag for organization
            metadata: Additional metadata

        Returns:
            ScreenshotInfo if successful, None otherwise
        """
        # Check cooldown
        current_time = datetime.now().timestamp() * 1000
        if current_time - self.last_capture_time < self.capture_cooldown:
            return None

        # Check max limit
        if len(self.screenshots) >= self.max_screenshots:
            # Remove oldest
            self.screenshots.pop(0)

        # Generate filename
        filename = self._generate_filename(tag)
        filepath = self.save_dir / filename

        # Save screenshot
        try:
            if self.format == "png":
                pg.image.save(surface, str(filepath))
            elif self.format == "jpg":
                pg.image.save(surface, str(filepath))
            else:
                pg.image.save(surface, str(filepath))

            # Create info
            info = ScreenshotInfo(
                filename=filename,
                filepath=str(filepath),
                timestamp=datetime.now().isoformat(),
                width=surface.get_width(),
                height=surface.get_height(),
                game_state=metadata or {},
                tags=[tag] if tag else [],
            )

            self.screenshots.append(info)
            self.last_capture_time = current_time

            # Save index
            self._save_index()

            return info

        except pg.error as e:
            print(f"Warning: Could not save screenshot: {e}")
            return None

    def capture_scaled(
        self, surface: pg.Surface, scale: float = 1.0, tag: str = "", metadata: Optional[dict] = None
    ) -> Optional[ScreenshotInfo]:
        """
        Capture scaled screenshot.

        Args:
            surface: Source surface
            scale: Scale factor (0-1 for smaller)
            tag: Optional tag
            metadata: Additional metadata

        Returns:
            ScreenshotInfo if successful
        """
        if scale == 1.0:
            return self.capture(surface, tag, metadata)

        new_width = int(surface.get_width() * scale)
        new_height = int(surface.get_height() * scale)

        scaled_surface = pg.transform.smoothscale(surface, (new_width, new_height))

        return self.capture(scaled_surface, tag, metadata)

    def get_screenshots(self) -> List[ScreenshotInfo]:
        """Get list of all screenshots."""
        return self.screenshots.copy()

    def get_screenshots_by_tag(self, tag: str) -> List[ScreenshotInfo]:
        """Get screenshots with specific tag."""
        return [ss for ss in self.screenshots if tag in ss.tags]

    def get_screenshots_by_date(self, date: str) -> List[ScreenshotInfo]:
        """
        Get screenshots from specific date.

        Args:
            date: Date string (YYYY-MM-DD)

        Returns:
            List of screenshots from that date
        """
        return [ss for ss in self.screenshots if ss.timestamp.startswith(date)]

    def delete_screenshot(self, filename: str) -> bool:
        """
        Delete a screenshot.

        Args:
            filename: Filename to delete

        Returns:
            True if deleted
        """
        for i, ss in enumerate(self.screenshots):
            if ss.filename == filename:
                try:
                    filepath = Path(ss.filepath)
                    if filepath.exists():
                        filepath.unlink()
                    self.screenshots.pop(i)
                    self._save_index()
                    return True
                except OSError:
                    return False
        return False

    def clear_all(self) -> None:
        """Delete all screenshots."""
        for ss in self.screenshots:
            try:
                filepath = Path(ss.filepath)
                if filepath.exists():
                    filepath.unlink()
            except OSError:
                pass

        self.screenshots.clear()
        self.screenshot_count = 0
        self._save_index()

    def _save_index(self) -> None:
        """Save screenshot index to file."""
        index_file = self.save_dir / "index.json"

        data = {
            "version": "1.0",
            "count": len(self.screenshots),
            "last_updated": datetime.now().isoformat(),
            "screenshots": [
                {
                    "filename": ss.filename,
                    "filepath": ss.filepath,
                    "timestamp": ss.timestamp,
                    "width": ss.width,
                    "height": ss.height,
                    "game_state": ss.game_state,
                    "tags": ss.tags,
                }
                for ss in self.screenshots
            ],
        }

        try:
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save screenshot index: {e}")

    def _load_index(self) -> None:
        """Load screenshot index from file."""
        index_file = self.save_dir / "index.json"

        if not index_file.exists():
            # Count existing files
            self.screenshot_count = len(list(self.save_dir.glob("*.png")))
            return

        try:
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.screenshot_count = data.get("count", 0)

            for ss_data in data.get("screenshots", []):
                self.screenshots.append(
                    ScreenshotInfo(
                        filename=ss_data["filename"],
                        filepath=ss_data["filepath"],
                        timestamp=ss_data["timestamp"],
                        width=ss_data["width"],
                        height=ss_data["height"],
                        game_state=ss_data.get("game_state", {}),
                        tags=ss_data.get("tags", []),
                    )
                )

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load screenshot index: {e}")

    def export_gallery(self, output_dir: str) -> int:
        """
        Export gallery to HTML.

        Args:
            output_dir: Output directory

        Returns:
            Number of screenshots exported
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Copy screenshots and create HTML
        html_content = self._generate_gallery_html()

        html_file = output_path / "gallery.html"
        try:
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            return len(self.screenshots)
        except IOError:
            return 0

    def _generate_gallery_html(self) -> str:
        """Generate HTML gallery content."""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mario Screenshots</title>
    <style>
        body { font-family: Arial; background: #1a1a2e; color: white; }
        .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; padding: 20px; }
        .screenshot { background: #16213e; border-radius: 8px; overflow: hidden; }
        .screenshot img { width: 100%; height: auto; }
        .info { padding: 10px; }
        .timestamp { color: #888; font-size: 12px; }
        .tags { color: #4ecca3; font-size: 12px; }
    </style>
</head>
<body>
    <h1 style="text-align: center; padding: 20px;">Super Mario Bros - Screenshots</h1>
    <div class="gallery">
"""

        for ss in reversed(self.screenshots):  # Newest first
            html += f"""
        <div class="screenshot">
            <img src="{ss.filename}" alt="{ss.filename}">
            <div class="info">
                <div class="timestamp">{ss.timestamp}</div>
                <div class="tags">{', '.join(ss.tags)}</div>
                <div>{ss.width}x{ss.height}</div>
            </div>
        </div>
"""

        html += """
    </div>
</body>
</html>
"""
        return html

    def get_stats(self) -> dict:
        """Get screenshot statistics."""
        total_size = 0
        for ss in self.screenshots:
            try:
                filepath = Path(ss.filepath)
                if filepath.exists():
                    total_size += filepath.stat().st_size
            except OSError:
                pass

        return {
            "count": len(self.screenshots),
            "total_size_mb": total_size / (1024 * 1024),
            "formats": {self.format: len(self.screenshots)},
            "directory": str(self.save_dir),
        }


class AutoScreenshot:
    """
    Automatic screenshot triggers.
    """

    def __init__(self, manager: ScreenshotManager) -> None:
        """
        Initialize auto screenshot.

        Args:
            manager: Screenshot manager
        """
        self.manager = manager
        self.triggers: Dict[str, bool] = {}
        self.counters: Dict[str, int] = {}

    def enable_trigger(self, trigger: str) -> None:
        """Enable auto-screenshot trigger."""
        self.triggers[trigger] = True
        self.counters[trigger] = 0

    def disable_trigger(self, trigger: str) -> None:
        """Disable auto-screenshot trigger."""
        self.triggers[trigger] = False

    def on_event(self, event: str, surface: pg.Surface) -> Optional[ScreenshotInfo]:
        """
        Handle game event.

        Args:
            event: Event name
            surface: Game surface

        Returns:
            ScreenshotInfo if captured
        """
        if not self.triggers.get(event, False):
            return None

        # Increment counter
        self.counters[event] = self.counters.get(event, 0) + 1

        return self.manager.capture(
            surface, tag=f"auto_{event}", metadata={"event": event, "count": self.counters[event]}
        )


# Common trigger names
AUTO_TRIGGERS = {
    "level_start": "Start of level",
    "level_complete": "Level completion",
    "powerup": "Power-up collected",
    "1up": "Extra life",
    "secret": "Secret found",
    "death": "Player death",
    "boss": "Boss encounter",
    "high_score": "New high score",
}
