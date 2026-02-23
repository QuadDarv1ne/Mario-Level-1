"""
Combo System Manager for Super Mario Bros.

Provides:
- Combo chain tracking
- Multiplier calculation
- Combo notifications
- Special combo rewards
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple, Dict, Any, Callable

import pygame as pg

from . import constants as c


class ComboType(Enum):
    """Types of combos."""

    ENEMY_STOMP = auto()
    FIREBALL_KILL = auto()
    SHELL_KILL = auto()
    COIN_COLLECT = auto()
    POWERUP_COLLECT = auto()
    PERFECT_JUMP = auto()
    LONG_JUMP = auto()
    TRIPLE_JUMP = auto()


@dataclass
class ComboEvent:
    """Represents a combo event."""

    combo_type: ComboType
    timestamp: float
    points: int
    position: Optional[Tuple[int, int]] = None


@dataclass
class ComboChain:
    """Represents an active combo chain."""

    combo_type: ComboType
    count: int = 0
    multiplier: float = 1.0
    start_time: float = 0.0
    last_hit_time: float = 0.0
    max_count: int = 0
    bonus_achieved: bool = False


@dataclass
class ComboStats:
    """Statistics for combo system."""

    total_combos: int = 0
    max_combo: int = 0
    total_multiplier_points: int = 0
    perfect_combos: int = 0
    combo_breaks: int = 0


class ComboManager:
    """
    Manages combo chains and multipliers.

    Usage:
        combo = ComboManager()
        combo.add_hit(ComboType.ENEMY_STOMP, position)
        multiplier = combo.get_multiplier()
    """

    # Combo windows in milliseconds
    COMBO_WINDOW = 2000  # 2 seconds to continue combo
    CHAIN_BONUS_THRESHOLD = 5  # Bonus at 5+ combo

    def __init__(self) -> None:
        """Initialize combo manager."""
        self.active_chains: Dict[ComboType, ComboChain] = {}
        self.current_combo: int = 0
        self.total_combo: int = 0
        self.stats = ComboStats()

        self.combo_events: List[ComboEvent] = []
        self.max_events = 10

        self.multiplier: float = 1.0
        self.last_hit_time: float = 0

        # Callbacks for combo events
        self.on_combo_start: Optional[Callable[[ComboType], None]] = None
        self.on_combo_update: Optional[Callable[[ComboType, int, float], None]] = None
        self.on_combo_end: Optional[Callable[[ComboType, int], None]] = None
        self.on_bonus: Optional[Callable[[str, int], None]] = None

        # Combo messages for display
        self.combo_messages: List[Tuple[str, float, Tuple[int, int]]] = []

    def add_hit(self, combo_type: ComboType, position: Optional[Tuple[int, int]] = None, base_points: int = 100) -> int:
        """
        Add a hit to the combo chain.

        Args:
            combo_type: Type of combo
            position: World position of the hit
            base_points: Base points for this action

        Returns:
            Total points earned (with multiplier)
        """
        current_time = time.time() * 1000  # ms

        # Check if continuing existing combo
        if combo_type in self.active_chains:
            chain = self.active_chains[combo_type]
            time_diff = current_time - chain.last_hit_time

            if time_diff <= self.COMBO_WINDOW:
                # Continue combo
                chain.count += 1
                chain.last_hit_time = current_time
                chain.multiplier = self._calculate_multiplier(chain.count)

                if chain.count > chain.max_count:
                    chain.max_count = chain.count

                self._on_combo_update(chain)
                self._add_combo_message(chain)

                # Check for bonus
                if chain.count == self.CHAIN_BONUS_THRESHOLD and not chain.bonus_achieved:
                    chain.bonus_achieved = True
                    self._trigger_bonus(chain)
            else:
                # Combo expired - start new one
                self._end_combo(chain)
                self._start_new_combo(combo_type, current_time)
        else:
            # Start new combo
            self._start_new_combo(combo_type, current_time)

        # Calculate points
        chain = self.active_chains[combo_type]
        points = int(base_points * chain.multiplier)

        # Add event
        event = ComboEvent(combo_type=combo_type, timestamp=current_time, points=points, position=position)
        self.combo_events.append(event)
        if len(self.combo_events) > self.max_events:
            self.combo_events.pop(0)

        # Update stats
        self.stats.total_combos += 1
        self.total_combo += 1
        if chain.count > self.stats.max_combo:
            self.stats.max_combo = chain.count

        self.stats.total_multiplier_points += points - base_points

        return points

    def _start_new_combo(self, combo_type: ComboType, current_time: float) -> None:
        """Start a new combo chain."""
        chain = ComboChain(combo_type=combo_type, count=1, start_time=current_time, last_hit_time=current_time)
        self.active_chains[combo_type] = chain

        if self.on_combo_start:
            self.on_combo_start(combo_type)

        self._add_combo_message(chain)

    def _end_combo(self, chain: ComboChain) -> None:
        """End a combo chain."""
        if chain.count >= self.CHAIN_BONUS_THRESHOLD:
            self.stats.perfect_combos += 1
        else:
            self.stats.combo_breaks += 1

        if self.on_combo_end:
            self.on_combo_end(chain.combo_type, chain.count)

        del self.active_chains[chain.combo_type]

    def _on_combo_update(self, chain: ComboChain) -> None:
        """Handle combo update."""
        if self.on_combo_update:
            self.on_combo_update(chain.combo_type, chain.count, chain.multiplier)

    def _calculate_multiplier(self, combo_count: int) -> float:
        """Calculate multiplier based on combo count."""
        if combo_count < 3:
            return 1.0
        elif combo_count < 5:
            return 1.5
        elif combo_count < 10:
            return 2.0
        elif combo_count < 20:
            return 3.0
        else:
            return 5.0

    def _trigger_bonus(self, chain: ComboChain) -> None:
        """Trigger combo bonus."""
        bonus_text = f"{chain.combo_type.name} BONUS!"
        bonus_points = chain.count * 500

        if self.on_bonus:
            self.on_bonus(bonus_text, bonus_points)

        self.combo_messages.append((f"🔥 {bonus_text} +{bonus_points}", time.time() * 1000, (0, 0)))  # Will be updated

    def _add_combo_message(self, chain: ComboChain) -> None:
        """Add combo display message."""
        if chain.count > 1:
            msg = f"Combo x{chain.count}!"
            if chain.multiplier > 1.0:
                msg += f" (x{chain.multiplier})"

            self.combo_messages.append((msg, time.time() * 1000, (0, 0)))

    def get_multiplier(self) -> float:
        """Get current total multiplier."""
        if not self.active_chains:
            return 1.0

        # Use highest multiplier from active chains
        return max(chain.multiplier for chain in self.active_chains.values())

    def get_current_combo(self) -> int:
        """Get current highest combo count."""
        if not self.active_chains:
            return 0
        return max(chain.count for chain in self.active_chains.values())

    def update(self) -> None:
        """Update combo system (check for expired combos)."""
        current_time = time.time() * 1000

        expired = []
        for combo_type, chain in self.active_chains.items():
            if current_time - chain.last_hit_time > self.COMBO_WINDOW:
                expired.append(combo_type)

        for combo_type in expired:
            self._end_combo(self.active_chains[combo_type])

        # Clean old messages
        self._cleanup_messages(current_time)

    def _cleanup_messages(self, current_time: float) -> None:
        """Remove old combo messages."""
        self.combo_messages = [
            (msg, ts, pos) for msg, ts, pos in self.combo_messages if current_time - ts < 2000  # 2 seconds
        ]

    def draw(self, surface: pg.Surface, position: Tuple[int, int] = (10, 100)) -> None:
        """
        Draw combo display.

        Args:
            surface: Surface to draw to
            position: Base position for display
        """
        if not self.combo_messages:
            return

        font = pg.font.Font(None, 28)
        small_font = pg.font.Font(None, 20)

        x, y = position
        line_height = 25

        for i, (msg, ts, _) in enumerate(self.combo_messages[-5:]):
            # Fade out effect
            age = (time.time() * 1000) - ts
            alpha = max(0, 255 - int(age / 2000 * 255))

            # Color based on combo size
            if "BONUS" in msg:
                color = c.GOLD
            elif "x5" in msg or "x10" in msg:
                color = c.RED
            else:
                color = c.WHITE

            # Create surface with alpha
            text_surface = font.render(msg, True, color)
            text_surface.set_alpha(alpha)

            draw_y = y + i * line_height
            surface.blit(text_surface, (x, draw_y))

        # Draw current multiplier
        multiplier = self.get_multiplier()
        if multiplier > 1.0:
            mult_surface = small_font.render(f"Multiplier: x{multiplier}", True, c.YELLOW)
            surface.blit(mult_surface, (x, y + 150))

    def reset(self) -> None:
        """Reset all combos."""
        for chain in list(self.active_chains.values()):
            self._end_combo(chain)

        self.current_combo = 0
        self.total_combo = 0
        self.multiplier = 1.0
        self.combo_events.clear()
        self.combo_messages.clear()

    def get_stats(self) -> ComboStats:
        """Get combo statistics."""
        return self.stats

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "total_combos": self.stats.total_combos,
            "max_combo": self.stats.max_combo,
            "perfect_combos": self.stats.perfect_combos,
            "total_multiplier_points": self.stats.total_multiplier_points,
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load from dictionary."""
        self.stats.total_combos = data.get("total_combos", 0)
        self.stats.max_combo = data.get("max_combo", 0)
        self.stats.perfect_combos = data.get("perfect_combos", 0)
        self.stats.total_multiplier_points = data.get("total_multiplier_points", 0)
