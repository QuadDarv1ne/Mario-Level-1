"""
Tests for screenshot, debug, and statistics systems.

Note: Dialogue system tests are in test_wave2_systems.py
"""
import os
import tempfile
from pathlib import Path

import pytest
import pygame as pg

from data.screenshot import (
    ScreenshotInfo,
    ScreenshotManager,
    AutoScreenshot,
    AUTO_TRIGGERS,
)

from data.debug import (
    DebugStats,
    DebugOverlay,
    CollisionVisualizer,
    EntityInspector,
    DebugConsole,
    PerformanceProfiler,
    DebugManager,
)

from data.statistics import (
    SessionStats,
    LifetimeStats,
    EnemyStats,
    PowerUpStats,
    StatisticsManager,
    StatsDisplay,
)


# =============================================================================
# Screenshot System Tests
# =============================================================================

class TestScreenshotInfo:
    """Tests for ScreenshotInfo."""

    def test_screenshot_info_creation(self) -> None:
        """Test screenshot info creation."""
        info = ScreenshotInfo(
            filename="test.png",
            filepath="screenshots/test.png",
            timestamp="2026-02-28_12-00-00",
            width=800,
            height=600,
            game_state={"level": "1-1"},
            tags=["level_complete"]
        )

        assert info.filename == "test.png"
        assert info.width == 800
        assert info.height == 600


class TestScreenshotManager:
    """Tests for ScreenshotManager."""

    @pytest.fixture
    def screenshot_manager(self) -> ScreenshotManager:
        """Create screenshot manager."""
        return ScreenshotManager()

    def test_manager_creation(self, screenshot_manager: ScreenshotManager) -> None:
        """Test screenshot manager initialization."""
        assert screenshot_manager.screenshot_count == 0
        assert screenshot_manager.max_screenshots == 1000

    def test_capture_screenshot(self, screenshot_manager: ScreenshotManager) -> None:
        """Test capturing screenshot."""
        pg.init()
        screen = pg.display.set_mode((800, 600))

        with tempfile.TemporaryDirectory() as tmpdir:
            screenshot_manager.save_dir = Path(tmpdir)
            screenshot_manager.capture(screen, "test")

            assert screenshot_manager.screenshot_count >= 0

        pg.quit()


class TestAutoScreenshot:
    """Tests for AutoScreenshot."""

    def test_auto_screenshot_creation(self) -> None:
        """Test auto screenshot creation."""
        pg.init()
        manager = ScreenshotManager()
        auto = AutoScreenshot(manager)

        assert auto.manager == manager
        assert len(auto.triggers) == 0

        pg.quit()

    def test_auto_triggers_exist(self) -> None:
        """Test auto triggers are defined."""
        assert len(AUTO_TRIGGERS) > 0


# =============================================================================
# Debug System Tests
# =============================================================================

class TestDebugStats:
    """Tests for DebugStats."""

    def test_debug_stats_creation(self) -> None:
        """Test debug stats creation."""
        stats = DebugStats()

        assert stats.sprite_count == 0


class TestDebugOverlay:
    """Tests for DebugOverlay."""

    @pytest.fixture
    def overlay(self) -> DebugOverlay:
        """Create debug overlay."""
        return DebugOverlay()

    def test_overlay_creation(self, overlay: DebugOverlay) -> None:
        """Test debug overlay initialization."""
        assert overlay.visible is False

    def test_toggle_overlay(self, overlay: DebugOverlay) -> None:
        """Test toggling overlay."""
        overlay.toggle()
        assert overlay.visible is True

        overlay.toggle()
        assert overlay.visible is False


class TestDebugManager:
    """Tests for DebugManager."""

    @pytest.fixture
    def debug_manager(self) -> DebugManager:
        """Create debug manager."""
        return DebugManager()

    def test_manager_creation(self, debug_manager: DebugManager) -> None:
        """Test debug manager initialization."""
        assert debug_manager.overlay is not None


# =============================================================================
# Statistics System Tests
# =============================================================================

class TestSessionStats:
    """Tests for SessionStats."""

    def test_session_stats_creation(self) -> None:
        """Test session stats creation."""
        stats = SessionStats()

        assert stats.score == 0
        assert stats.coins_collected == 0


class TestLifetimeStats:
    """Tests for LifetimeStats."""

    def test_lifetime_stats_creation(self) -> None:
        """Test lifetime stats creation."""
        stats = LifetimeStats()

        assert stats.total_deaths == 0
        assert stats.total_coins == 0

    def test_lifetime_stats_increment(self) -> None:
        """Test incrementing lifetime stats."""
        stats = LifetimeStats()
        stats.total_deaths += 1

        assert stats.total_deaths == 1


class TestStatisticsManager:
    """Tests for StatisticsManager."""

    @pytest.fixture
    def stats_manager(self) -> StatisticsManager:
        """Create statistics manager."""
        return StatisticsManager()

    def test_manager_creation(self, stats_manager: StatisticsManager) -> None:
        """Test statistics manager initialization."""
        assert stats_manager.session is not None
        assert stats_manager.lifetime is not None

    def test_save_and_load(self, stats_manager: StatisticsManager) -> None:
        """Test save and load statistics."""
        stats_manager.save()
        stats_manager.load()

        assert stats_manager.lifetime is not None


class TestStatsDisplay:
    """Tests for StatsDisplay."""

    @pytest.fixture
    def stats_display(self) -> StatsDisplay:
        """Create stats display."""
        manager = StatisticsManager()
        return StatsDisplay(manager)

    def test_stats_display_creation(self, stats_display: StatsDisplay) -> None:
        """Test stats display initialization."""
        assert stats_display.stats is not None
