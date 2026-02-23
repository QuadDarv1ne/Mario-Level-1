"""
Tests for achievements system.
"""
import json
import os
import tempfile
from pathlib import Path

import pytest

from data.achievements import (
    Achievement,
    AchievementTier,
    AchievementsManager,
    AchievementsUI,
    AchievementNotification,
)


class TestAchievement:
    """Tests for Achievement dataclass."""

    def test_create_achievement(self) -> None:
        """Test creating a basic achievement."""
        ach = Achievement(
            id="test_ach",
            name="Test Achievement",
            description="Test description",
        )

        assert ach.id == "test_ach"
        assert ach.name == "Test Achievement"
        assert ach.description == "Test description"
        assert ach.tier == AchievementTier.BRONZE
        assert ach.points == 10
        assert ach.unlocked is False
        assert ach.progress == 0
        assert ach.requirement == 1

    def test_achievement_to_dict(self) -> None:
        """Test serialization to dictionary."""
        ach = Achievement(
            id="test_ach",
            name="Test",
            description="Desc",
            tier=AchievementTier.GOLD,
            points=25,
        )

        data = ach.to_dict()

        assert data["id"] == "test_ach"
        assert data["name"] == "Test"
        assert data["tier"] == "gold"
        assert data["points"] == 25

    def test_achievement_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "id": "test_ach",
            "name": "Test",
            "description": "Desc",
            "tier": "silver",
            "points": 15,
            "unlocked": True,
            "progress": 5,
            "requirement": 10,
        }

        ach = Achievement.from_dict(data)

        assert ach.id == "test_ach"
        assert ach.tier == AchievementTier.SILVER
        assert ach.points == 15
        assert ach.unlocked is True
        assert ach.progress == 5

    def test_add_progress_unlocks(self) -> None:
        """Test that adding progress unlocks achievement."""
        ach = Achievement(
            id="test_ach",
            name="Test",
            description="Desc",
            requirement=5,
        )

        # Add progress but don't unlock yet
        assert ach.add_progress(3) is False
        assert ach.progress == 3
        assert ach.unlocked is False

        # Unlock
        assert ach.add_progress(2) is True
        assert ach.progress == 5
        assert ach.unlocked is True
        assert ach.unlocked_at is not None

    def test_add_progress_already_unlocked(self) -> None:
        """Test adding progress to already unlocked achievement."""
        ach = Achievement(
            id="test_ach",
            name="Test",
            description="Desc",
            unlocked=True,
            progress=10,
        )

        assert ach.add_progress(5) is False
        assert ach.progress == 10  # Should not change

    def test_get_progress_percent(self) -> None:
        """Test progress percentage calculation."""
        ach = Achievement(
            id="test_ach",
            name="Test",
            description="Desc",
            progress=5,
            requirement=10,
        )

        assert ach.get_progress_percent() == 50.0

        ach.progress = 15
        assert ach.get_progress_percent() == 100.0  # Capped at 100


class TestAchievementsManager:
    """Tests for AchievementsManager."""

    @pytest.fixture
    def temp_save_dir(self) -> str:
        """Create temporary directory for saves."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def manager(self, temp_save_dir: str) -> AchievementsManager:
        """Create achievements manager with temp save directory."""
        return AchievementsManager(save_dir=temp_save_dir)

    def test_init_creates_achievements(self, manager: AchievementsManager) -> None:
        """Test that initialization creates default achievements."""
        assert len(manager.achievements) > 0
        assert "first_coin" in manager.achievements
        assert "first_stomp" in manager.achievements

    def test_init_statistics(self, manager: AchievementsManager) -> None:
        """Test that statistics are initialized."""
        assert "coins_collected" in manager.statistics
        assert manager.statistics["coins_collected"] == 0

    def test_increment_statistic(self, manager: AchievementsManager) -> None:
        """Test incrementing statistics."""
        manager.increment("coins_collected", 5)
        assert manager.statistics["coins_collected"] == 5

        manager.increment("coins_collected", 3)
        assert manager.statistics["coins_collected"] == 8

    def test_increment_invalid_statistic(self, manager: AchievementsManager) -> None:
        """Test incrementing non-existent statistic."""
        initial = manager.statistics["coins_collected"]
        manager.increment("invalid_stat", 10)
        assert manager.statistics["coins_collected"] == initial

    def test_unlock_achievement(self, manager: AchievementsManager) -> None:
        """Test manually unlocking achievement."""
        result = manager.unlock("first_coin")

        assert result is True
        assert manager.achievements["first_coin"].unlocked is True
        assert manager.total_points > 0

    def test_unlock_already_unlocked(self, manager: AchievementsManager) -> None:
        """Test unlocking already unlocked achievement."""
        manager.unlock("first_coin")
        initial_points = manager.total_points

        result = manager.unlock("first_coin")

        assert result is False
        assert manager.total_points == initial_points  # Points not added again

    def test_unlock_invalid_achievement(self, manager: AchievementsManager) -> None:
        """Test unlocking non-existent achievement."""
        result = manager.unlock("invalid_achievement")
        assert result is False

    def test_save_and_load(self, manager: AchievementsManager, temp_save_dir: str) -> None:
        """Test saving and loading achievements."""
        # Modify some data
        manager.unlock("first_coin")
        manager.increment("coins_collected", 10)

        # Save
        manager.save()

        # Create new manager and load
        new_manager = AchievementsManager(save_dir=temp_save_dir)
        new_manager.load()

        assert new_manager.achievements["first_coin"].unlocked is True
        assert new_manager.statistics["coins_collected"] == 10

    def test_get_completion_percentage(self, manager: AchievementsManager) -> None:
        """Test completion percentage calculation."""
        # Initially 0%
        assert manager.get_completion_percentage() == 0.0

        # Unlock one achievement
        manager.unlock("first_coin")

        total = len(manager.achievements)
        expected = (1 / total) * 100
        assert abs(manager.get_completion_percentage() - expected) < 0.01

    def test_get_unlocked_achievements(self, manager: AchievementsManager) -> None:
        """Test getting unlocked achievements list."""
        unlocked = manager.get_unlocked_achievements()
        assert len(unlocked) == 0

        manager.unlock("first_coin")
        manager.unlock("first_stomp")

        unlocked = manager.get_unlocked_achievements()
        assert len(unlocked) == 2

    def test_get_locked_achievements(self, manager: AchievementsManager) -> None:
        """Test getting locked achievements list."""
        locked = manager.get_locked_achievements()
        assert len(locked) == len(manager.achievements)

        manager.unlock("first_coin")

        locked = manager.get_locked_achievements()
        assert len(locked) == len(manager.achievements) - 1

    def test_get_stat(self, manager: AchievementsManager) -> None:
        """Test getting statistic value."""
        assert manager.get_stat("coins_collected") == 0

        manager.increment("coins_collected", 5)
        assert manager.get_stat("coins_collected") == 5

    def test_get_stat_invalid(self, manager: AchievementsManager) -> None:
        """Test getting non-existent statistic."""
        assert manager.get_stat("invalid_stat") == 0

    def test_reset_statistics(self, manager: AchievementsManager) -> None:
        """Test resetting statistics."""
        manager.increment("coins_collected", 10)
        manager.increment("enemies_defeated", 5)

        manager.reset_statistics()

        assert manager.statistics["coins_collected"] == 0
        assert manager.statistics["enemies_defeated"] == 0

    def test_achievement_notifications(self, manager: AchievementsManager) -> None:
        """Test achievement notifications."""
        assert len(manager.notifications) == 0

        manager.unlock("first_coin")

        assert len(manager.notifications) == 1
        assert manager.notifications[0].achievement.id == "first_coin"

    def test_update_notifications(self, manager: AchievementsManager) -> None:
        """Test notification timer update."""
        manager.unlock("first_coin")
        assert len(manager.notifications) == 1

        # Expire notification (default timer is 3000ms)
        manager.update_notifications(3500)

        assert len(manager.notifications) == 0

    def test_get_tier_completion(self, manager: AchievementsManager) -> None:
        """Test tier completion calculation."""
        completion = manager.get_tier_completion()

        assert "bronze" in completion
        assert "silver" in completion
        assert "gold" in completion

        # All should be 0% initially
        for tier_percent in completion.values():
            assert tier_percent == 0.0


class TestAchievementNotifications:
    """Tests for achievement notifications."""

    def test_notification_creation(self) -> None:
        """Test creating achievement notification."""
        ach = Achievement(
            id="test",
            name="Test",
            description="Desc",
        )

        notification = AchievementNotification(ach)

        assert notification.achievement == ach
        assert notification.timer == 3000
        assert notification.alpha == 255
        assert notification.visible is True


class TestAchievementsIntegration:
    """Integration tests for achievements system."""

    @pytest.fixture
    def temp_save_dir(self) -> str:
        """Create temporary directory for saves."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_coin_collection_achievements(self, temp_save_dir: str) -> None:
        """Test coin-related achievements unlock correctly."""
        manager = AchievementsManager(save_dir=temp_save_dir)

        # Collect first coin
        manager.increment("coins_collected", 1)
        assert manager.achievements["first_coin"].unlocked is True

        # Collect more coins
        manager.increment("coins_collected", 49)
        assert manager.achievements["coin_collector"].unlocked is True

        # Not enough for coin_master yet
        assert manager.achievements["coin_master"].unlocked is False

    def test_enemy_defeat_achievements(self, temp_save_dir: str) -> None:
        """Test enemy defeat achievements unlock correctly."""
        manager = AchievementsManager(save_dir=temp_save_dir)

        # First stomp
        manager.increment("enemies_defeated", 1)
        manager.increment("goombas_defeated", 1)
        assert manager.achievements["first_stomp"].unlocked is True

        # More goombas
        manager.increment("goombas_defeated", 19)
        assert manager.achievements["goomba_hunter"].unlocked is True

    def test_persistence_across_sessions(self, temp_save_dir: str) -> None:
        """Test that achievements persist across game sessions."""
        # Session 1
        manager1 = AchievementsManager(save_dir=temp_save_dir)
        manager1.unlock("first_coin")
        manager1.increment("coins_collected", 25)
        manager1.save()

        # Session 2 (new manager instance)
        manager2 = AchievementsManager(save_dir=temp_save_dir)

        assert manager2.achievements["first_coin"].unlocked is True
        assert manager2.statistics["coins_collected"] == 25
        assert manager2.total_points == manager1.total_points
