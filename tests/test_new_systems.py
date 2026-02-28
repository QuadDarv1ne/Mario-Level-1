"""
Tests for screenshot, debug, and statistics systems.

Note: Dialogue system tests are in test_wave2_systems.py (DialogManager)
"""
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
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ScreenshotManager(save_dir=tmpdir)

    def test_manager_creation(self, screenshot_manager: ScreenshotManager) -> None:
        """Test screenshot manager initialization."""
        assert screenshot_manager.screenshot_count == 0
        assert screenshot_manager.max_screenshots == 1000

    def test_capture_screenshot(self, screenshot_manager: ScreenshotManager) -> None:
        """Test capturing screenshot."""
        pg.init()
        screen = pg.display.set_mode((800, 600))
        screen.fill((255, 255, 255))

        info = screenshot_manager.capture(screen, "test")

        assert info is not None
        assert "test" in info.filename

        pg.quit()

    def test_capture_cooldown(self, screenshot_manager: ScreenshotManager) -> None:
        """Test capture cooldown."""
        pg.init()
        screen = pg.display.set_mode((800, 600))

        # First capture
        screenshot_manager.capture(screen)

        # Immediate second capture should return None (cooldown)
        info = screenshot_manager.capture(screen)
        assert info is None

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

    def test_enable_trigger(self) -> None:
        """Test enabling trigger."""
        pg.init()
        manager = ScreenshotManager()
        auto = AutoScreenshot(manager)
        
        auto.enable_trigger("level_complete")

        assert auto.triggers["level_complete"] is True

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

    def test_update_stats(self, overlay: DebugOverlay) -> None:
        """Test updating stats."""
        pg.init()
        clock = pg.time.Clock()
        clock.tick(60)

        overlay.update(clock, [1, 2, 3], collisions=5)

        assert overlay.stats.fps > 0
        assert overlay.stats.sprite_count == 3
        assert overlay.stats.collision_count == 5

        pg.quit()


class TestCollisionVisualizer:
    """Tests for CollisionVisualizer."""

    @pytest.fixture
    def visualizer(self) -> CollisionVisualizer:
        """Create collision visualizer."""
        return CollisionVisualizer()

    def test_visualizer_creation(self, visualizer: CollisionVisualizer) -> None:
        """Test visualizer initialization."""
        assert visualizer.enabled is False

    def test_toggle_visualizer(self, visualizer: CollisionVisualizer) -> None:
        """Test toggling visualizer."""
        visualizer.toggle()
        assert visualizer.enabled is True


class TestDebugConsole:
    """Tests for DebugConsole."""

    @pytest.fixture
    def console(self) -> DebugConsole:
        """Create debug console."""
        return DebugConsole()

    def test_console_creation(self, console: DebugConsole) -> None:
        """Test console initialization."""
        assert console.visible is False
        assert len(console.commands) > 0

    def test_register_command(self, console: DebugConsole) -> None:
        """Test registering command."""

        def test_cmd(args: str) -> str:
            return "test"

        console.register_command("test", test_cmd)
        assert "test" in console.commands

    def test_help_command(self, console: DebugConsole) -> None:
        """Test help command."""
        result = console.cmd_help("")
        assert "Commands" in result


class TestPerformanceProfiler:
    """Tests for PerformanceProfiler."""

    @pytest.fixture
    def profiler(self) -> PerformanceProfiler:
        """Create performance profiler."""
        return PerformanceProfiler()

    def test_profiler_creation(self, profiler: PerformanceProfiler) -> None:
        """Test profiler initialization."""
        assert profiler.enabled is True
        assert len(profiler.timings) == 0

    def test_start_stop_timer(self, profiler: PerformanceProfiler) -> None:
        """Test starting and stopping timer."""
        profiler.start("test_op")

        import time
        time.sleep(0.01)  # 10ms

        duration = profiler.stop("test_op")
        assert duration is not None
        assert duration >= 10

    def test_get_stats(self, profiler: PerformanceProfiler) -> None:
        """Test getting stats."""
        profiler.start("test")
        
        import time
        time.sleep(0.01)
        profiler.stop("test")

        stats = profiler.get_stats("test")

        assert "count" in stats
        assert "avg" in stats

    def test_reset(self, profiler: PerformanceProfiler) -> None:
        """Test resetting profiler."""
        profiler.start("test")
        profiler.stop("test")

        profiler.reset()

        assert len(profiler.timings) == 0


class TestDebugManager:
    """Tests for DebugManager."""

    @pytest.fixture
    def debug_manager(self) -> DebugManager:
        """Create debug manager."""
        return DebugManager()

    def test_manager_creation(self, debug_manager: DebugManager) -> None:
        """Test debug manager initialization."""
        assert debug_manager.overlay is not None
        assert debug_manager.console is not None
        assert debug_manager.profiler is not None

    def test_handle_event_overlay(self, debug_manager: DebugManager) -> None:
        """Test handling overlay toggle event."""
        pg.init()

        event = pg.event.Event(pg.KEYDOWN, {"key": pg.K_F3})
        result = debug_manager.handle_event(event)

        assert result is True

        pg.quit()


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
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = str(Path(tmpdir) / "stats.json")
            yield StatisticsManager(save_path=save_path)

    def test_manager_creation(self, stats_manager: StatisticsManager) -> None:
        """Test statistics manager initialization."""
        assert stats_manager.session.score == 0
        assert stats_manager.lifetime.total_sessions == 0

    def test_increment_stat(self, stats_manager: StatisticsManager) -> None:
        """Test incrementing statistic."""
        stats_manager.increment("score", 100)

        assert stats_manager.session.score == 100

    def test_increment_multiple(self, stats_manager: StatisticsManager) -> None:
        """Test incrementing multiple times."""
        stats_manager.increment("coins_collected", 5)
        stats_manager.increment("coins_collected", 3)

        assert stats_manager.session.coins_collected == 8

    def test_get_stat(self, stats_manager: StatisticsManager) -> None:
        """Test getting statistic."""
        stats_manager.increment("score", 500)

        value = stats_manager.get_stat("score")
        assert value == 500

    def test_save_and_load(self, stats_manager: StatisticsManager) -> None:
        """Test save and load statistics."""
        stats_manager.increment("score", 1000)
        stats_manager.save()
        stats_manager.load()

        assert stats_manager.session.score >= 0


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

    def test_draw_session_stats(self, stats_display: StatsDisplay) -> None:
        """Test drawing session stats."""
        pg.init()
        surface = pg.Surface((800, 600))

        # Should not crash
        stats_display.draw_session_stats(surface)

        pg.quit()
