"""
Achievements system for Super Mario Bros.

Provides:
- Achievement definitions and tracking
- Progress persistence
- Unlock notifications
- Statistics tracking
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

import pygame as pg

from . import constants as c


class AchievementTier(Enum):
    """Achievement difficulty tiers."""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    LEGENDARY = "legendary"


@dataclass
class Achievement:
    """
    Represents a single achievement.

    Attributes:
        id: Unique identifier
        name: Display name
        description: What you need to do
        tier: Difficulty tier
        points: Points awarded
        icon: Icon name/sprite key
        unlocked: Whether it's unlocked
        progress: Current progress (0 to requirement)
        requirement: Required amount to unlock
        unlocked_at: Timestamp when unlocked
    """

    id: str
    name: str
    description: str
    tier: AchievementTier = AchievementTier.BRONZE
    points: int = 10
    icon: str = "star"
    unlocked: bool = False
    progress: int = 0
    requirement: int = 1
    unlocked_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tier": self.tier.value,
            "points": self.points,
            "icon": self.icon,
            "unlocked": self.unlocked,
            "progress": self.progress,
            "requirement": self.requirement,
            "unlocked_at": self.unlocked_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Achievement:
        """Create Achievement from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            tier=AchievementTier(data.get("tier", "bronze")),
            points=data.get("points", 10),
            icon=data.get("icon", "star"),
            unlocked=data.get("unlocked", False),
            progress=data.get("progress", 0),
            requirement=data.get("requirement", 1),
            unlocked_at=data.get("unlocked_at"),
        )

    def add_progress(self, amount: int = 1) -> bool:
        """
        Add progress to achievement.

        Args:
            amount: Amount to add

        Returns:
            True if achievement was just unlocked
        """
        if self.unlocked:
            return False

        self.progress += amount
        if self.progress >= self.requirement and not self.unlocked:
            self.unlocked = True
            self.unlocked_at = datetime.now().isoformat()
            return True
        return False

    def get_progress_percent(self) -> float:
        """Get progress as percentage (0-100)."""
        if self.requirement <= 0:
            return 100.0
        return min(100.0, (self.progress / self.requirement) * 100)


@dataclass
class AchievementNotification:
    """Pending achievement notification to display."""

    achievement: Achievement
    timer: int = 3000  # Display for 3 seconds
    alpha: int = 255
    visible: bool = True


class AchievementsManager:
    """
    Manages all achievements and statistics.

    Usage:
        achievements = AchievementsManager()
        achievements.load()
        achievements.increment("coins_collected", 5)
        achievements.save()
    """

    # Default achievements definitions
    DEFAULT_ACHIEVEMENTS: List[Achievement] = [
        # Coin achievements
        Achievement(
            id="first_coin",
            name="Первая монета",
            description="Соберите первую монету",
            tier=AchievementTier.BRONZE,
            points=5,
            icon="coin",
            requirement=1,
        ),
        Achievement(
            id="coin_collector",
            name="Коллекционер монет",
            description="Соберите 50 монет",
            tier=AchievementTier.SILVER,
            points=15,
            icon="coin_bag",
            requirement=50,
        ),
        Achievement(
            id="coin_master",
            name="Мастер монет",
            description="Соберите 100 монет за одну игру",
            tier=AchievementTier.GOLD,
            points=25,
            icon="crown",
            requirement=100,
        ),
        Achievement(
            id="millionaire",
            name="Миллионер",
            description="Соберите 500 монет всего",
            tier=AchievementTier.PLATINUM,
            points=50,
            icon="diamond",
            requirement=500,
        ),
        # Enemy stomp achievements
        Achievement(
            id="first_stomp",
            name="Первая победа",
            description="Победите первого врага",
            tier=AchievementTier.BRONZE,
            points=5,
            icon="boot",
            requirement=1,
        ),
        Achievement(
            id="goomba_hunter",
            name="Охотник на Гумб",
            description="Победите 20 гумб",
            tier=AchievementTier.SILVER,
            points=15,
            icon="goomba_mask",
            requirement=20,
        ),
        Achievement(
            id="koopa_crusher",
            name="Разрушитель Куп",
            description="Победите 10 куп",
            tier=AchievementTier.SILVER,
            points=15,
            icon="shell",
            requirement=10,
        ),
        Achievement(
            id="enemy_slayer",
            name="Убийца врагов",
            description="Победите 100 врагов всего",
            tier=AchievementTier.GOLD,
            points=30,
            icon="sword",
            requirement=100,
        ),
        Achievement(
            id="unstoppable",
            name="Неудержимый",
            description="Победите 10 врагов без получения урона",
            tier=AchievementTier.PLATINUM,
            points=50,
            icon="fire",
            requirement=10,
        ),
        # Power-up achievements
        Achievement(
            id="super_mario",
            name="Супер Марио",
            description="Возьмите первый гриб",
            tier=AchievementTier.BRONZE,
            points=10,
            icon="mushroom",
            requirement=1,
        ),
        Achievement(
            id="fire_power",
            name="Огненная сила",
            description="Возьмите огненный цветок",
            tier=AchievementTier.SILVER,
            points=15,
            icon="fireflower",
            requirement=1,
        ),
        Achievement(
            id="star_power",
            name="Звёздная сила",
            description="Возьмите звезду",
            tier=AchievementTier.SILVER,
            points=20,
            icon="star",
            requirement=1,
        ),
        # Score achievements
        Achievement(
            id="high_scorer",
            name="Рекордсмен",
            description="Наберите 10000 очков",
            tier=AchievementTier.SILVER,
            points=20,
            icon="trophy",
            requirement=10000,
        ),
        Achievement(
            id="score_master",
            name="Мастер очков",
            description="Наберите 50000 очков за одну игру",
            tier=AchievementTier.GOLD,
            points=35,
            icon="golden_trophy",
            requirement=50000,
        ),
        # Level completion
        Achievement(
            id="level_complete",
            name="Уровень пройден",
            description="Завершите уровень 1-1",
            tier=AchievementTier.SILVER,
            points=25,
            icon="flag",
            requirement=1,
        ),
        Achievement(
            id="speedrunner",
            name="Спидраннер",
            description="Завершите уровень за менее чем 100 секунд",
            tier=AchievementTier.GOLD,
            points=40,
            icon="clock",
            requirement=1,
        ),
        Achievement(
            id="no_damage_run",
            name="Без урона",
            description="Завершите уровень не получив урон",
            tier=AchievementTier.PLATINUM,
            points=75,
            icon="shield",
            requirement=1,
        ),
        Achievement(
            id="perfect_run",
            name="Идеальный забег",
            description="Завершите уровень со 100+ монетами и без урона",
            tier=AchievementTier.LEGENDARY,
            points=100,
            icon="rainbow_star",
            requirement=1,
        ),
        # Combo achievements
        Achievement(
            id="double_kill",
            name="Двойной удар",
            description="Победите 2 врагов подряд за 5 секунд",
            tier=AchievementTier.BRONZE,
            points=10,
            icon="double",
            requirement=1,
        ),
        Achievement(
            id="combo_master",
            name="Комбо мастер",
            description="Победите 5 врагов подряд за 10 секунд",
            tier=AchievementTier.GOLD,
            points=40,
            icon="combo",
            requirement=1,
        ),
        # Miscellaneous
        Achievement(
            id="explorer",
            name="Исследователь",
            description="Найдите секретный блок",
            tier=AchievementTier.BRONZE,
            points=10,
            icon="question",
            requirement=1,
        ),
        Achievement(
            id="lucky",
            name="Счастливчик",
            description="Получите жизнь (1UP)",
            tier=AchievementTier.SILVER,
            points=20,
            icon="clover",
            requirement=1,
        ),
    ]

    def __init__(self, save_dir: str = "saves") -> None:
        """
        Initialize achievements manager.

        Args:
            save_dir: Directory to save achievement data
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.save_file = self.save_dir / "achievements.json"

        self.achievements: Dict[str, Achievement] = {}
        self.statistics: Dict[str, int] = {}
        self.notifications: List[AchievementNotification] = []
        self.total_points: int = 0

        self._initialize()

    def _initialize(self) -> None:
        """Initialize achievements and load saved data."""
        # Create fresh achievements from defaults.  We can't reuse the
        # same objects because managers may be created multiple times (e.g.
        # during testing) and sharing would lead to unlocked/progress state
        # leaking between instances.
        for achievement in self.DEFAULT_ACHIEVEMENTS:
            # serialize+deserialize to make a deep copy
            self.achievements[achievement.id] = Achievement.from_dict(achievement.to_dict())

        # Initialize statistics
        self._init_statistics()

        # Load saved data
        self.load()

    def _init_statistics(self) -> None:
        """Initialize statistics tracking."""
        self.statistics = {
            "coins_collected": 0,
            "coins_total": 0,
            "enemies_defeated": 0,
            "goombas_defeated": 0,
            "koopas_defeated": 0,
            "powerups_collected": 0,
            "mushrooms_collected": 0,
            "fireflowers_collected": 0,
            "stars_collected": 0,
            "blocks_hit": 0,
            "secrets_found": 0,
            "lives_gained": 0,
            "levels_completed": 0,
            "deaths": 0,
            "damage_taken": 0,
            "fireballs_thrown": 0,
            "highest_score": 0,
            "total_playtime": 0,
            "combo_count": 0,
            "max_combo": 0,
        }

    def load(self) -> None:
        """Load achievements and statistics from file."""
        if not self.save_file.exists():
            return

        try:
            with open(self.save_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load achievements
            for ach_data in data.get("achievements", []):
                achievement = Achievement.from_dict(ach_data)
                if achievement.id in self.achievements:
                    self.achievements[achievement.id] = achievement

            # Load statistics
            saved_stats = data.get("statistics", {})
            for key, value in saved_stats.items():
                if key in self.statistics:
                    self.statistics[key] = value

            # Calculate total points
            self.total_points = sum(ach.points for ach in self.achievements.values() if ach.unlocked)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load achievements: {e}")

    def save(self) -> None:
        """Save achievements and statistics to file."""
        data = {
            "achievements": [ach.to_dict() for ach in self.achievements.values()],
            "statistics": self.statistics,
            "total_points": self.total_points,
            "last_updated": datetime.now().isoformat(),
        }

        try:
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save achievements: {e}")

    def increment(self, stat_name: str, amount: int = 1) -> None:
        """
        Increment a statistic and check related achievements.

        Args:
            stat_name: Name of statistic to increment
            amount: Amount to add
        """
        if stat_name not in self.statistics:
            return

        self.statistics[stat_name] += amount
        self._check_achievements(stat_name)

    def _check_achievements(self, stat_name: str) -> None:
        """
        Check achievements related to a statistic.

        Args:
            stat_name: Statistic that was updated
        """
        achievement_map = {
            "coins_collected": ["first_coin", "coin_collector", "coin_master", "millionaire"],
            "goombas_defeated": ["goomba_hunter"],
            "koopas_defeated": ["koopa_crusher"],
            # first_stomp unlocks on any enemy defeat
            "enemies_defeated": ["first_stomp", "enemy_slayer", "unstoppable"],
            "mushrooms_collected": ["super_mario"],
            "fireflowers_collected": ["fire_power"],
            "stars_collected": ["star_power"],
            "highest_score": ["high_scorer", "score_master"],
            "levels_completed": ["level_complete"],
            "secrets_found": ["explorer"],
            "lives_gained": ["lucky"],
        }

        if stat_name in achievement_map:
            for ach_id in achievement_map[stat_name]:
                if ach_id in self.achievements:
                    ach = self.achievements[ach_id]
                    stat_value = self.statistics[stat_name]

                    if ach.add_progress(stat_value - ach.progress):
                        self._on_achievement_unlocked(ach)
                        self.total_points += ach.points

    def unlock(self, achievement_id: str) -> bool:
        """
        Manually unlock an achievement.

        Args:
            achievement_id: ID of achievement to unlock

        Returns:
            True if achievement was unlocked
        """
        if achievement_id not in self.achievements:
            return False

        ach = self.achievements[achievement_id]
        if not ach.unlocked:
            ach.unlocked = True
            ach.unlocked_at = datetime.now().isoformat()
            ach.progress = ach.requirement
            self._on_achievement_unlocked(ach)
            self.total_points += ach.points
            return True
        return False

    def _on_achievement_unlocked(self, achievement: Achievement) -> None:
        """
        Handle achievement unlock.

        Args:
            achievement: The unlocked achievement
        """
        self.notifications.append(AchievementNotification(achievement))

    def update_notifications(self, dt: int) -> None:
        """
        Update achievement notifications.

        Args:
            dt: Delta time in milliseconds
        """
        for notification in self.notifications[:]:
            notification.timer -= dt
            if notification.timer <= 0:
                self.notifications.remove(notification)

    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Get achievement by ID."""
        return self.achievements.get(achievement_id)

    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        return [ach for ach in self.achievements.values() if ach.unlocked]

    def get_locked_achievements(self) -> List[Achievement]:
        """Get all locked achievements."""
        return [ach for ach in self.achievements.values() if not ach.unlocked]

    def get_completion_percentage(self) -> float:
        """Get overall completion percentage."""
        if not self.achievements:
            return 0.0
        unlocked = len(self.get_unlocked_achievements())
        return (unlocked / len(self.achievements)) * 100

    def get_tier_completion(self) -> Dict[str, float]:
        """Get completion percentage per tier."""
        tiers: Dict[str, List[Achievement]] = {}
        for ach in self.achievements.values():
            tier_name = ach.tier.value
            if tier_name not in tiers:
                tiers[tier_name] = []
            tiers[tier_name].append(ach)

        result = {}
        for tier_name, achievements in tiers.items():
            unlocked = sum(1 for a in achievements if a.unlocked)
            result[tier_name] = (unlocked / len(achievements)) * 100 if achievements else 0

        return result

    def get_stat(self, stat_name: str) -> int:
        """Get statistic value."""
        return self.statistics.get(stat_name, 0)

    def reset_statistics(self) -> None:
        """Reset all statistics (keep achievements)."""
        self._init_statistics()
        self.save()


class AchievementsUI:
    """
    UI renderer for achievements system.
    """

    def __init__(self, manager: AchievementsManager) -> None:
        """
        Initialize achievements UI.

        Args:
            manager: Achievements manager instance
        """
        self.manager = manager
        self.font_large: Optional[pg.font.Font] = None
        self.font_small: Optional[pg.font.Font] = None
        self._init_fonts()

    def _init_fonts(self) -> None:
        """Initialize fonts."""
        try:
            self.font_large = pg.font.Font(None, 36)
            self.font_small = pg.font.Font(None, 24)
        except pg.error:
            self.font_large = None
            self.font_small = None

    def draw_notification(self, surface: pg.Surface, notification: AchievementNotification) -> None:
        """
        Draw achievement unlock notification.

        Args:
            surface: Surface to draw to
            notification: Notification to draw
        """
        ach = notification.achievement

        # Calculate position (top-right corner)
        padding = 20
        width = 350
        height = 80
        x = surface.get_width() - width - padding
        y = padding

        # Create background
        bg_surface = pg.Surface((width, height), pg.SRCALPHA)

        # Color based on tier
        tier_colors = {
            AchievementTier.BRONZE: (205, 127, 50, 240),
            AchievementTier.SILVER: (192, 192, 192, 240),
            AchievementTier.GOLD: (255, 215, 0, 240),
            AchievementTier.PLATINUM: (229, 228, 226, 240),
            AchievementTier.LEGENDARY: (180, 100, 255, 240),
        }
        color = tier_colors.get(ach.tier, (255, 215, 0, 240))

        # Draw rounded rectangle background
        pg.draw.rect(bg_surface, color, (0, 0, width, height), border_radius=10)
        pg.draw.rect(bg_surface, (*color[:3], 255), (0, 0, width, height), 2, border_radius=10)
        bg_surface.set_alpha(notification.alpha)

        surface.blit(bg_surface, (x, y))

        # Draw text
        if self.font_large and self.font_small:
            # Title
            title = f"🏆 {ach.name}!"
            title_surface = self.font_large.render(title, True, c.BLACK)
            surface.blit(title_surface, (x + 60, y + 10))

            # Description
            desc_surface = self.font_small.render(ach.description, True, c.NAVYBLUE)
            surface.blit(desc_surface, (x + 60, y + 40))

            # Points
            points_surface = self.font_small.render(f"+{ach.points} очков", True, c.GREEN)
            surface.blit(points_surface, (x + 60, y + 60))

        # Draw icon placeholder
        icon_rect = pg.Rect(x + 15, y + 20, 35, 35)
        pg.draw.rect(surface, c.GOLD, icon_rect)
        pg.draw.rect(surface, c.BLACK, icon_rect, 2)

    def draw_all_notifications(self, surface: pg.Surface) -> None:
        """
        Draw all active notifications.

        Args:
            surface: Surface to draw to
        """
        for i, notification in enumerate(self.manager.notifications):
            _ = i * 90  # offset_y reserved for future use
            # Temporarily adjust position
            _ = notification.timer  # original_y reserved for future use
            self.draw_notification(surface, notification)

    def draw_achievements_screen(self, surface: pg.Surface) -> None:
        """
        Draw full achievements list screen.

        Args:
            surface: Surface to draw to
        """
        surface.fill(c.BGCOLOR)

        y_offset = 20
        x_padding = 20

        # Title
        if self.font_large:
            title = f"Достижения ({self.manager.get_completion_percentage():.1f}%)"
            title_surface = self.font_large.render(title, True, c.BLACK)
            surface.blit(title_surface, (x_padding, y_offset))
            y_offset += 50

        # Draw achievements list
        if self.font_small:
            for ach in self.manager.achievements.values():
                color = c.GOLD if ach.unlocked else c.GRAY
                status = "✓" if ach.unlocked else "🔒"

                text = f"{status} {ach.name} - {ach.description} ({ach.progress}/{ach.requirement})"
                text_surface = self.font_small.render(text, True, color)
                surface.blit(text_surface, (x_padding + 20, y_offset))
                y_offset += 30
