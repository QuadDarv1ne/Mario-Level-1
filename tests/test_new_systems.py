"""
Tests for dialogue, screenshot, debug, and statistics systems.
"""
import os
import tempfile
from pathlib import Path

import pytest
import pygame as pg

from data.dialogue_system import (
    DialogueAlign,
    DialogueSpeed,
    DialogueLine,
    Character,
    DialogueBox,
    DialogueManager,
    StoryProgression,
    MARIO_DIALOGUES,
    create_default_dialogues,
)

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
# Dialogue System Tests
# =============================================================================

class TestDialogueLine:
    """Tests for DialogueLine."""

    def test_dialogue_line_creation(self) -> None:
        """Test creating dialogue line."""
        line = DialogueLine(
            speaker="Mario",
            text="Let's-a go!"
        )

        assert line.speaker == "Mario"
        assert line.text == "Let's-a go!"
        assert line.align == DialogueAlign.LEFT
        assert line.speed == DialogueSpeed.NORMAL

    def test_dialogue_line_with_options(self) -> None:
        """Test dialogue line with custom options."""
        line = DialogueLine(
            speaker="Mario",
            text="Hello!",
            align=DialogueAlign.CENTER,
            speed=DialogueSpeed.FAST,
            next_id="line_2"
        )

        assert line.align == DialogueAlign.CENTER
        assert line.speed == DialogueSpeed.FAST
        assert line.next_id == "line_2"


class TestCharacter:
    """Tests for Character."""

    def test_character_creation(self) -> None:
        """Test creating character."""
        char = Character(
            name="mario",
            display_name="Марио",
            color=(255, 0, 0)
        )

        assert char.name == "mario"
        assert char.display_name == "Марио"
        assert char.color == (255, 0, 0)


class TestDialogueBox:
    """Tests for DialogueBox."""

    @pytest.fixture
    def dialogue_box(self) -> DialogueBox:
        """Create dialogue box."""
        return DialogueBox(50, 400, 700, 150)

    def test_dialogue_box_creation(self, dialogue_box: DialogueBox) -> None:
        """Test dialogue box initialization."""
        assert dialogue_box.visible is False
        assert dialogue_box.is_typing is False
        assert dialogue_box.alpha == 0

    def test_show_dialogue(self, dialogue_box: DialogueBox) -> None:
        """Test showing dialogue."""
        line = DialogueLine(speaker="Test", text="Hello World")
        dialogue_box.show(line)

        assert dialogue_box.visible is True
        assert dialogue_box.is_typing is True

    def test_update_typewriter(self, dialogue_box: DialogueBox) -> None:
        """Test typewriter effect."""
        line = DialogueLine(
            speaker="Test",
            text="Hello",
            speed=DialogueSpeed.INSTANT
        )
        dialogue_box.show(line)
        dialogue_box.update(100)

        assert dialogue_box.displayed_text == "Hello"
        assert dialogue_box.is_complete is True

    def test_advance_dialogue(self, dialogue_box: DialogueBox) -> None:
        """Test advancing dialogue."""
        line = DialogueLine(
            speaker="Test",
            text="Hello World",
            speed=DialogueSpeed.INSTANT
        )
        dialogue_box.show(line)
        dialogue_box.update(100)

        result = dialogue_box.advance()
        # Should return True to continue

    def test_hide_dialogue(self, dialogue_box: DialogueBox) -> None:
        """Test hiding dialogue."""
        dialogue_box.show(DialogueLine(speaker="Test", text="Test"))
        dialogue_box.hide()

        assert dialogue_box.visible is False


class TestDialogueManager:
    """Tests for DialogueManager."""

    @pytest.fixture
    def dialogue_manager(self) -> DialogueManager:
        """Create dialogue manager."""
        return DialogueManager()

    def test_manager_creation(self, dialogue_manager: DialogueManager) -> None:
        """Test dialogue manager initialization."""
        assert dialogue_manager.is_active is False
        assert dialogue_manager.current_id is None

    def test_register_dialogue(self, dialogue_manager: DialogueManager) -> None:
        """Test registering dialogue."""
        line = DialogueLine(speaker="Test", text="Test")
        dialogue_manager.register_dialogue("test_id", line)

        assert "test_id" in dialogue_manager.dialogues

    def test_start_dialogue(self, dialogue_manager: DialogueManager) -> None:
        """Test starting dialogue."""
        line = DialogueLine(
            speaker="Test",
            text="Test",
            next_id=None
        )
        dialogue_manager.register_dialogue("start", line)

        result = dialogue_manager.start("start")
        assert result is True
        assert dialogue_manager.is_active is True

    def test_start_invalid_dialogue(self, dialogue_manager: DialogueManager) -> None:
        """Test starting invalid dialogue."""
        result = dialogue_manager.start("nonexistent")
        assert result is False

    def test_end_dialogue(self, dialogue_manager: DialogueManager) -> None:
        """Test ending dialogue."""
        dialogue_manager.is_active = True
        dialogue_manager.end()

        assert dialogue_manager.is_active is False
        assert dialogue_manager.current_id is None

    def test_create_default_dialogues(self) -> None:
        """Test creating default dialogues."""
        manager = create_default_dialogues()

        assert len(manager.dialogues) > 0
        assert "intro_1" in manager.dialogues


class TestStoryProgression:
    """Tests for StoryProgression."""

    @pytest.fixture
    def story(self) -> StoryProgression:
        """Create story progression."""
        return StoryProgression()

    def test_story_creation(self, story: StoryProgression) -> None:
        """Test story progression initialization."""
        assert story.current_chapter == "prologue"
        assert len(story.completed_events) == 0

    def test_mark_event_complete(self, story: StoryProgression) -> None:
        """Test marking event complete."""
        story.mark_event_complete("first_jump")

        assert story.is_event_complete("first_jump") is True

    def test_set_flag(self, story: StoryProgression) -> None:
        """Test setting story flag."""
        story.set_flag("met_toad", True)

        assert story.get_flag("met_toad") is True

    def test_set_variable(self, story: StoryProgression) -> None:
        """Test setting story variable."""
        story.set_variable("coins_found", 10)

        assert story.get_variable("coins_found") == 10

    def test_increment_variable(self, story: StoryProgression) -> None:
        """Test incrementing variable."""
        story.set_variable("count", 5)
        result = story.increment_variable("count", 3)

        assert result == 8

    def test_get_progress(self, story: StoryProgression) -> None:
        """Test getting progress."""
        story.mark_event_complete("test")
        story.set_flag("flag1", True)

        progress = story.get_progress()

        assert "chapter" in progress
        assert "events_completed" in progress


# =============================================================================
# Screenshot System Tests
# =============================================================================

class TestScreenshotInfo:
    """Tests for ScreenshotInfo."""

    def test_screenshot_info_creation(self) -> None:
        """Test creating screenshot info."""
        info = ScreenshotInfo(
            filename="test.png",
            filepath="/test/test.png",
            timestamp="2024-01-01",
            width=800,
            height=600
        )

        assert info.filename == "test.png"
        assert info.width == 800
        assert info.height == 600


class TestScreenshotManager:
    """Tests for ScreenshotManager."""

    @pytest.fixture
    def screenshot_mgr(self) -> ScreenshotManager:
        """Create screenshot manager with temp dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ScreenshotManager(save_dir=tmpdir)

    def test_manager_creation(self, screenshot_mgr: ScreenshotManager) -> None:
        """Test screenshot manager initialization."""
        assert screenshot_mgr.format == "png"
        assert screenshot_mgr.auto_number is True

    def test_capture_screenshot(self, screenshot_mgr: ScreenshotManager) -> None:
        """Test capturing screenshot."""
        pg.init()
        surface = pg.Surface((800, 600))
        surface.fill(c.WHITE)

        info = screenshot_mgr.capture(surface, tag="test")

        assert info is not None
        assert "test" in info.filename
        assert len(screenshot_mgr.get_screenshots()) == 1

        pg.quit()

    def test_capture_cooldown(self, screenshot_mgr: ScreenshotManager) -> None:
        """Test capture cooldown."""
        pg.init()
        surface = pg.Surface((800, 600))

        # First capture
        screenshot_mgr.capture(surface)

        # Immediate second capture should return None
        info = screenshot_mgr.capture(surface)
        assert info is None

        pg.quit()

    def test_get_screenshots_by_tag(self, screenshot_mgr: ScreenshotManager) -> None:
        """Test getting screenshots by tag."""
        pg.init()
        surface = pg.Surface((800, 600))

        screenshot_mgr.capture(surface, tag="level1")
        screenshot_mgr.capture(surface, tag="level2")

        level1_screens = screenshot_mgr.get_screenshots_by_tag("level1")
        assert len(level1_screens) == 1

        pg.quit()

    def test_get_stats(self, screenshot_mgr: ScreenshotManager) -> None:
        """Test getting stats."""
        stats = screenshot_mgr.get_stats()

        assert "count" in stats
        assert "total_size_mb" in stats
        assert "directory" in stats


class TestAutoScreenshot:
    """Tests for AutoScreenshot."""

    @pytest.fixture
    def auto_screenshot(self) -> tuple[AutoScreenshot, ScreenshotManager]:
        """Create auto screenshot system."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScreenshotManager(save_dir=tmpdir)
            auto = AutoScreenshot(mgr)
            yield auto, mgr

    def test_enable_trigger(self, auto_screenshot: tuple) -> None:
        """Test enabling trigger."""
        auto, _ = auto_screenshot
        auto.enable_trigger("level_complete")

        assert auto.triggers["level_complete"] is True

    def test_on_event_triggered(self, auto_screenshot: tuple) -> None:
        """Test event triggering screenshot."""
        auto, mgr = auto_screenshot
        auto.enable_trigger("powerup")

        pg.init()
        surface = pg.Surface((800, 600))

        info = auto.on_event("powerup", surface)
        assert info is not None

        pg.quit()

    def test_on_event_not_triggered(self, auto_screenshot: tuple) -> None:
        """Test event not triggering when disabled."""
        auto, mgr = auto_screenshot

        pg.init()
        surface = pg.Surface((800, 600))

        info = auto.on_event("powerup", surface)
        assert info is None  # Not enabled

        pg.quit()


# =============================================================================
# Debug System Tests
# =============================================================================

class TestDebugStats:
    """Tests for DebugStats."""

    def test_debug_stats_creation(self) -> None:
        """Test debug stats initialization."""
        stats = DebugStats()

        assert stats.fps == 0.0
        assert stats.sprite_count == 0


class TestDebugOverlay:
    """Tests for DebugOverlay."""

    @pytest.fixture
    def debug_overlay(self) -> DebugOverlay:
        """Create debug overlay."""
        return DebugOverlay()

    def test_overlay_creation(self, debug_overlay: DebugOverlay) -> None:
        """Test overlay initialization."""
        assert debug_overlay.visible is False
        assert debug_overlay.stats.fps == 0.0

    def test_toggle_overlay(self, debug_overlay: DebugOverlay) -> None:
        """Test toggling overlay."""
        initial = debug_overlay.visible
        debug_overlay.toggle()
        assert debug_overlay.visible != initial

    def test_update_stats(self, debug_overlay: DebugOverlay) -> None:
        """Test updating stats."""
        pg.init()
        clock = pg.time.Clock()
        clock.tick(60)

        debug_overlay.update(clock, [1, 2, 3], collisions=5)

        assert debug_overlay.stats.fps > 0
        assert debug_overlay.stats.sprite_count == 3
        assert debug_overlay.stats.collision_count == 5

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

    def test_execute_command(self, console: DebugConsole) -> None:
        """Test executing command."""
        console.input_text = "help"
        console._execute_command()

        assert len(console.output) > 0

    def test_help_command(self, console: DebugConsole) -> None:
        """Test help command."""
        result = console.cmd_help("")
        assert "Commands" in result

    def test_clear_command(self, console: DebugConsole) -> None:
        """Test clear command."""
        console.output.append("test")
        result = console.cmd_clear("")

        assert result == "Console cleared"
        assert len(console.output) == 0


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

        event = pg.event.Event(pg.KEYDOWN, {'key': pg.K_F3})
        result = debug_manager.handle_event(event)

        assert result is True
        assert debug_manager.overlay.visible != False

        pg.quit()


# =============================================================================
# Statistics System Tests
# =============================================================================

class TestSessionStats:
    """Tests for SessionStats."""

    def test_session_stats_creation(self) -> None:
        """Test session stats initialization."""
        stats = SessionStats()

        assert stats.score == 0
        assert stats.coins_collected == 0
        assert stats.deaths == 0


class TestLifetimeStats:
    """Tests for LifetimeStats."""

    def test_lifetime_stats_creation(self) -> None:
        """Test lifetime stats initialization."""
        stats = LifetimeStats()

        assert stats.total_sessions == 0
        assert stats.highest_score == 0


class TestStatisticsManager:
    """Tests for StatisticsManager."""

    @pytest.fixture
    def stats_manager(self) -> StatisticsManager:
        """Create statistics manager with temp file."""
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

    def test_get_stat_default(self, stats_manager: StatisticsManager) -> None:
        """Test getting statistic with default."""
        value = stats_manager.get_stat("nonexistent", default=-1)
        assert value == -1

    def test_save_and_load(self, stats_manager: StatisticsManager) -> None:
        """Test saving and loading statistics."""
        stats_manager.increment("score", 1000)
        stats_manager.increment("lifetime.total_score", 5000)
        stats_manager.save()

        # Create new manager and load
        new_manager = StatisticsManager(save_path=stats_manager.save_path)
        new_manager.load()

        assert new_manager.lifetime.total_score > 0

    def test_get_session_summary(self, stats_manager: StatisticsManager) -> None:
        """Test getting session summary."""
        stats_manager.increment("score", 500)
        stats_manager.increment("coins_collected", 10)
        stats_manager.increment("enemies_defeated", 5)

        summary = stats_manager.get_session_summary()

        assert "score" in summary
        assert "coins" in summary
        assert "kdr" in summary

    def test_get_lifetime_summary(self, stats_manager: StatisticsManager) -> None:
        """Test getting lifetime summary."""
        stats_manager.lifetime.total_sessions = 5
        stats_manager.lifetime.total_playtime_seconds = 3600

        summary = stats_manager.get_lifetime_summary()

        assert "sessions" in summary
        assert "playtime_hours" in summary

    def test_reset_all(self, stats_manager: StatisticsManager) -> None:
        """Test resetting all statistics."""
        stats_manager.increment("score", 1000)
        stats_manager.reset_all()

        assert stats_manager.session.score == 0


class TestStatsDisplay:
    """Tests for StatsDisplay."""

    @pytest.fixture
    def stats_manager(self) -> StatisticsManager:
        """Create statistics manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield StatisticsManager(save_path=str(Path(tmpdir) / "stats.json"))

    @pytest.fixture
    def stats_display(self, stats_manager: StatisticsManager) -> StatsDisplay:
        """Create stats display."""
        return StatsDisplay(stats_manager)

    def test_display_creation(
        self,
        stats_display: StatsDisplay,
        stats_manager: StatisticsManager
    ) -> None:
        """Test stats display initialization."""
        assert stats_display.stats == stats_manager

    def test_draw_session_stats(
        self,
        stats_display: StatsDisplay
    ) -> None:
        """Test drawing session stats."""
        pg.init()
        surface = pg.Surface((800, 600))

        # Should not crash
        stats_display.draw_session_stats(surface)

        pg.quit()


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for new systems."""

    def test_dialogue_with_story_progression(self) -> None:
        """Test dialogue system with story progression."""
        manager = create_default_dialogues()
        story = StoryProgression()

        # Start dialogue
        manager.start("intro_1")
        manager.update(16)

        # Mark event complete
        story.mark_event_complete("started_game")

        assert story.is_event_complete("started_game")

    def test_screenshot_with_stats(self) -> None:
        """Test screenshot system with statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ss_mgr = ScreenshotManager(save_dir=tmpdir)
            stats_mgr = StatisticsManager(save_path=str(Path(tmpdir) / "stats.json"))

            pg.init()
            surface = pg.Surface((800, 600))

            # Capture on stat milestone
            stats_mgr.increment("score", 1000)
            if stats_mgr.get_stat("score") >= 1000:
                ss_mgr.capture(surface, tag="milestone")

            assert len(ss_mgr.get_screenshots()) >= 1

            pg.quit()

    def test_debug_with_statistics(self) -> None:
        """Test debug system with statistics."""
        debug_mgr = DebugManager()
        stats_mgr = StatisticsManager()

        # Update debug with sprite count from stats
        sprites = list(range(10))
        debug_mgr.update(sprites=sprites)

        assert debug_mgr.overlay.stats.sprite_count == 10

    def test_full_game_session(self) -> None:
        """Test complete game session simulation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stats_mgr = StatisticsManager(save_path=str(Path(tmpdir) / "stats.json"))
            ss_mgr = ScreenshotManager(save_dir=tmpdir)
            dialogue_mgr = create_default_dialogues()

            pg.init()
            surface = pg.Surface((800, 600))

            # Simulate gameplay
            stats_mgr.increment("jumps", 10)
            stats_mgr.increment("coins_collected", 25)
            stats_mgr.increment("enemies_defeated", 5)

            # Trigger dialogue
            dialogue_mgr.start("intro_1")
            dialogue_mgr.update(16)

            # Take screenshot
            ss_mgr.capture(surface, tag="gameplay")

            # Save stats
            stats_mgr.save()

            # Verify
            summary = stats_mgr.get_session_summary()
            assert summary["coins"] == 25
            assert len(ss_mgr.get_screenshots()) >= 1

            pg.quit()
