"""
Enhanced Hint System for Super Mario Bros.

Features:
- Context-sensitive hints
- Tutorial mode
- Progressive hint disclosure
- Hint categories
- Achievement-based unlocks
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple, Dict, Any, Callable

import pygame as pg

from . import constants as c


class HintCategory(Enum):
    """Hint categories."""

    CONTROLS = auto()
    COMBAT = auto()
    POWERUPS = auto()
    SECRETS = auto()
    ENEMIES = auto()
    ADVANCED = auto()


class HintTrigger(Enum):
    """Hint trigger types."""

    ON_START = auto()
    ON_DEATH = auto()
    ON_POWERUP = auto()
    ON_ENEMY_KILL = auto()
    ON_SECRET_FOUND = auto()
    ON_FIRST_JUMP = auto()
    ON_COMBO = auto()
    MANUAL = auto()


@dataclass
class Hint:
    """Represents a hint."""

    id: str
    text: str
    category: HintCategory
    trigger: HintTrigger
    priority: int = 1  # 1-5, 5 is highest
    shown: bool = False
    show_count: int = 0
    prerequisites: List[str] = field(default_factory=list)
    context_keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "category": self.category.name,
            "trigger": self.trigger.name,
            "priority": self.priority,
            "shown": self.shown,
            "show_count": self.show_count,
            "prerequisites": self.prerequisites,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Hint":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            text=data["text"],
            category=HintCategory[data["category"]],
            trigger=HintTrigger[data["trigger"]],
            priority=data.get("priority", 1),
            shown=data.get("shown", False),
            show_count=data.get("show_count", 0),
            prerequisites=data.get("prerequisites", []),
            context_keywords=data.get("context_keywords", []),
        )


class HintManager:
    """
    Manages hints and tutorials.

    Features:
    - Context-sensitive hint display
    - Progressive disclosure
    - Persistence
    - Tutorial mode
    """

    # Built-in hints database
    DEFAULT_HINTS: List[Dict[str, Any]] = [
        # Controls
        {
            "id": "controls_move",
            "text": "Используйте стрелки ← → для движения Марио",
            "category": "CONTROLS",
            "trigger": "ON_START",
            "priority": 5,
        },
        {
            "id": "controls_jump",
            "text": "Нажмите 'A' для прыжка. Удерживайте для更高 прыжка!",
            "category": "CONTROLS",
            "trigger": "ON_FIRST_JUMP",
            "priority": 5,
        },
        {
            "id": "controls_run",
            "text": "Зажмите 'S' для бега. Бег + прыжок = дальний прыжок!",
            "category": "CONTROLS",
            "trigger": "MANUAL",
            "priority": 3,
        },
        {
            "id": "controls_crouch",
            "text": "Нажмите вниз, чтобы присесть. Полезно в низких проходах!",
            "category": "CONTROLS",
            "trigger": "MANUAL",
            "priority": 2,
        },
        # Combat
        {
            "id": "combat_stomp",
            "text": "Прыгайте на врагов сверху, чтобы победить их!",
            "category": "COMBAT",
            "trigger": "ON_ENEMY_KILL",
            "priority": 4,
        },
        {
            "id": "combat_shell",
            "text": "Панцирь черепахи можно использовать как оружие!",
            "category": "COMBAT",
            "trigger": "MANUAL",
            "priority": 3,
        },
        {
            "id": "combat_combo",
            "text": "Побеждайте врагов подряд для комбо-множителя очков!",
            "category": "COMBAT",
            "trigger": "ON_COMBO",
            "priority": 3,
        },
        # Powerups
        {
            "id": "powerup_mushroom",
            "text": "Гриб делает Марио большим и позволяет разбивать кирпичи!",
            "category": "POWERUPS",
            "trigger": "ON_POWERUP",
            "priority": 4,
        },
        {
            "id": "powerup_flower",
            "text": "Огонь позволяет стрелять файерболами! Нажмите 'S' для выстрела.",
            "category": "POWERUPS",
            "trigger": "ON_POWERUP",
            "priority": 4,
        },
        {
            "id": "powerup_star",
            "text": "Звезда даёт неуязвимость! Бегите и уничтожайте всё!",
            "category": "POWERUPS",
            "trigger": "ON_POWERUP",
            "priority": 5,
        },
        # Enemies
        {
            "id": "enemy_goomba",
            "text": "Гумба идут прямо. Просто прыгайте на них!",
            "category": "ENEMIES",
            "trigger": "MANUAL",
            "priority": 2,
        },
        {
            "id": "enemy_koopa",
            "text": "Черепахи прячутся в панцирь при прыжке. Осторожно!",
            "category": "ENEMIES",
            "trigger": "MANUAL",
            "priority": 3,
        },
        {
            "id": "enemy_piranha",
            "text": "Растения появляются из труб. Не подходите, когда они открыты!",
            "category": "ENEMIES",
            "trigger": "MANUAL",
            "priority": 3,
        },
        # Secrets
        {
            "id": "secret_blocks",
            "text": "Некоторые блоки скрыты! Прыгайте под неизвестные блоки.",
            "category": "SECRETS",
            "trigger": "ON_SECRET_FOUND",
            "priority": 4,
        },
        {
            "id": "secret_vines",
            "text": "Иногда из блоков растут лианы. Они ведут к бонусам!",
            "category": "SECRETS",
            "trigger": "MANUAL",
            "priority": 3,
        },
        # Advanced
        {
            "id": "advanced_wall_jump",
            "text": "Прыжок от стены возможен в некоторых местах!",
            "category": "ADVANCED",
            "trigger": "MANUAL",
            "priority": 1,
        },
        {
            "id": "advanced_speed",
            "text": "Наберите скорость для сверхдальних прыжков!",
            "category": "ADVANCED",
            "trigger": "MANUAL",
            "priority": 2,
        },
    ]

    def __init__(self, save_path: str = "saves/hints.json", tutorial_mode: bool = True) -> None:
        """
        Initialize hint manager.

        Args:
            save_path: Path to save hint progress
            tutorial_mode: Enable tutorial mode
        """
        self.save_path = save_path
        self.tutorial_mode = tutorial_mode

        self.hints: Dict[str, Hint] = {}
        self.hint_queue: List[Hint] = []
        self.current_hint: Optional[Hint] = None

        # Display settings
        self.hint_visible = False
        self.hint_display_time = 5000  # ms
        self.hint_timer: float = 0

        # Statistics
        self.stats = {
            "total_shown": 0,
            "hints_discovered": 0,
            "tutorial_progress": 0.0,
        }

        # Callbacks
        self.on_hint_show: Optional[Callable[[Hint], None]] = None
        self.on_hint_hide: Optional[Callable[[Hint], None]] = None

        # Load hints
        self._load_hints()

    def _load_hints(self) -> None:
        """Load hints from database and save file."""
        # Load default hints
        for hint_data in self.DEFAULT_HINTS:
            hint = Hint.from_dict(hint_data)
            self.hints[hint.id] = hint

        # Load progress from save
        self._load_progress()

    def _load_progress(self) -> None:
        """Load hint progress from save file."""
        if not os.path.exists(self.save_path):
            return

        try:
            with open(self.save_path, "r") as f:
                data = json.load(f)

            for hint_id, hint_data in data.get("hints", {}).items():
                if hint_id in self.hints:
                    self.hints[hint_id].shown = hint_data.get("shown", False)
                    self.hints[hint_id].show_count = hint_data.get("show_count", 0)
        except (json.JSONDecodeError, IOError):
            pass

    def save_progress(self) -> None:
        """Save hint progress."""
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

        data = {
            "hints": {hint.id: hint.to_dict() for hint in self.hints.values()},
            "stats": self.stats,
        }

        with open(self.save_path, "w") as f:
            json.dump(data, f, indent=2)

    def on_event(self, event_type: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Notify hint system of game event.

        Args:
            event_type: Event type (matches HintTrigger)
            context: Additional context
        """
        trigger = HintTrigger[event_type]

        # Find applicable hints
        available = self._get_available_hints(trigger, context)

        if available:
            # Add to queue
            self.hint_queue.extend(available)

    def _get_available_hints(self, trigger: HintTrigger, context: Optional[Dict[str, Any]] = None) -> List[Hint]:
        """Get hints available for trigger."""
        available = []

        for hint in self.hints.values():
            if hint.trigger != trigger:
                continue

            if hint.shown and hint.show_count >= 3:
                continue  # Don't show too many times

            if hint.prerequisites:
                if not all(
                    self.hints.get(p, Hint("", "", HintCategory.CONTROLS, trigger)).shown for p in hint.prerequisites
                ):
                    continue  # Prerequisites not met

            # Context matching
            if context and hint.context_keywords:
                if not any(kw in str(context) for kw in hint.context_keywords):
                    continue

            available.append(hint)

        # Sort by priority
        available.sort(key=lambda h: h.priority, reverse=True)
        return available

    def update(self, dt: float) -> Optional[Hint]:
        """
        Update hint system.

        Args:
            dt: Delta time in ms

        Returns:
            Current hint if displaying
        """
        current_time = time.time() * 1000

        # Hide timer
        if self.hint_visible and self.current_hint:
            if current_time - self.hint_timer > self.hint_display_time:
                self.hide_hint()

        # Show next hint if queue has items
        if not self.hint_visible and self.hint_queue:
            hint = self.hint_queue.pop(0)
            self.show_hint(hint)

        return self.current_hint

    def show_hint(self, hint: Hint) -> None:
        """Show a hint."""
        self.current_hint = hint
        self.hint_visible = True
        self.hint_timer = time.time() * 1000

        hint.shown = True
        hint.show_count += 1

        self.stats["total_shown"] += 1
        self._update_tutorial_progress()

        if self.on_hint_show:
            self.on_hint_show(hint)

    def hide_hint(self) -> None:
        """Hide current hint."""
        if self.current_hint and self.on_hint_hide:
            self.on_hint_hide(self.current_hint)

        self.hint_visible = False
        self.current_hint = None

    def force_show_hint(self, hint_id: str) -> bool:
        """
        Force show a specific hint.

        Args:
            hint_id: Hint ID to show

        Returns:
            True if hint was found and shown
        """
        if hint_id in self.hints:
            hint = self.hints[hint_id]
            self.hint_queue.insert(0, hint)
            return True
        return False

    def get_hint(self, hint_id: str) -> Optional[Hint]:
        """Get hint by ID."""
        return self.hints.get(hint_id)

    def get_hints_by_category(self, category: HintCategory, only_shown: bool = False) -> List[Hint]:
        """Get hints by category."""
        hints = [h for h in self.hints.values() if h.category == category]

        if only_shown:
            hints = [h for h in hints if h.shown]

        return hints

    def get_unshown_hints(self) -> List[Hint]:
        """Get all unshown hints."""
        return [h for h in self.hints.values() if not h.shown]

    def _update_tutorial_progress(self) -> None:
        """Update tutorial progress percentage."""
        total = len(self.hints)
        shown = sum(1 for h in self.hints.values() if h.shown)
        self.stats["tutorial_progress"] = shown / total if total > 0 else 0

    def get_tutorial_progress(self) -> float:
        """Get tutorial progress (0.0 to 1.0)."""
        return self.stats["tutorial_progress"]

    def draw(self, surface: pg.Surface, position: Tuple[int, int] = None) -> None:
        """
        Draw current hint.

        Args:
            surface: Surface to draw to
            position: Position (default: bottom center)
        """
        if not self.hint_visible or not self.current_hint:
            return

        if position is None:
            position = (surface.get_width() // 2, surface.get_height() - 80)

        x, y = position

        # Create background
        font = pg.font.Font(None, 24)
        text = self.current_hint.text

        # Word wrap
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < 600:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        if current_line:
            lines.append(current_line)

        # Calculate size
        line_height = 28
        padding = 20
        width = 640
        height = len(lines) * line_height + padding * 2

        # Background
        bg_surface = pg.Surface((width, height), pg.SRCALPHA)
        bg_surface.fill((0, 0, 0, 200))
        pg.draw.rect(bg_surface, c.GOLD, (0, 0, width, height), 2)

        surface.blit(bg_surface, (x - width // 2, y - height // 2))

        # Text
        for i, line in enumerate(lines):
            text_surface = font.render(line.strip(), True, c.WHITE)
            surface.blit(text_surface, (x - text_surface.get_width() // 2, y - height // 2 + padding + i * line_height))

        # Hint counter
        if self.current_hint.show_count > 1:
            counter_surface = font.render(f"({self.current_hint.show_count}/3)", True, c.GRAY)
            surface.blit(counter_surface, (x + width // 2 - 60, y + height // 2 - 25))

    def reset(self) -> None:
        """Reset all hint progress."""
        for hint in self.hints.values():
            hint.shown = False
            hint.show_count = 0

        self.stats["total_shown"] = 0
        self.stats["tutorial_progress"] = 0.0
        self.hint_queue.clear()
        self.hide_hint()

    def get_stats(self) -> Dict[str, Any]:
        """Get hint statistics."""
        return {
            **self.stats,
            "total_hints": len(self.hints),
            "unshown_hints": len(self.get_unshown_hints()),
        }
