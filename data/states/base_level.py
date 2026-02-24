"""
Base class for game levels.

Provides common functionality for all level states.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

import pygame as pg

from .. import tools
from .. import constants as c
from ..components import mario as mario_module

if TYPE_CHECKING:
    from ..components.info import OverheadInfo


class BaseLevel(tools._State):
    """
    Base class for all level states.

    Provides common methods and attributes for level management.
    Subclasses should override:
        - setup_background()
        - setup_ground()
        - setup_enemies()
        - setup_mario()
        - And other setup methods as needed
    """

    def __init__(self) -> None:
        super().__init__()
        self.game_info: Dict[str, Any] = {}
        self.persist: Dict[str, Any] = {}

        # Timing
        self.death_timer: float = 0
        self.flag_timer: float = 0
        self.flag_score: Optional[Any] = None

        # Sprite groups
        self.moving_score_list: List[Any] = []
        self.overhead_info_display: Optional[OverheadInfo] = None

        # Display
        self.background: Optional[pg.Surface] = None
        self.back_rect: Optional[pg.Rect] = None
        self.level: Optional[pg.Surface] = None
        self.level_rect: Optional[pg.Rect] = None
        self.viewport: Optional[pg.Rect] = None

        # Sprite groups - initialized by subclasses
        self.ground_group: Optional[pg.sprite.Group] = None
        self.pipe_group: Optional[pg.sprite.Group] = None
        self.step_group: Optional[pg.sprite.Group] = None
        self.brick_group: Optional[pg.sprite.Group] = None
        self.coin_box_group: Optional[pg.sprite.Group] = None
        self.flag_pole_group: Optional[pg.sprite.Group] = None
        self.enemy_group: Optional[pg.sprite.Group] = None
        self.mario: Optional[mario_module.Mario] = None
        self.checkpoint_group: Optional[pg.sprite.Group] = None
        self.flag: Optional[Any] = None
        self.pole: Optional[Any] = None
        self.finial: Optional[Any] = None
        self.coin_group: Optional[pg.sprite.Group] = None
        self.powerup_group: Optional[pg.sprite.Group] = None
        self.fire_group: Optional[pg.sprite.Group] = None

    def startup(self, current_time: float, persist: Dict[str, Any]) -> None:
        """Called when the State object is created."""
        self.game_info = persist
        self.persist = self.game_info
        self.game_info[c.CURRENT_TIME] = current_time
        self.game_info[c.LEVEL_STATE] = c.NOT_FROZEN
        self.game_info[c.MARIO_DEAD] = False

        self.state = c.NOT_FROZEN
        self.start_time = current_time

    def create_overhead_display(self) -> None:
        """Create the overhead info display."""
        from ..components.info import OverheadInfo

        self.overhead_info_display = OverheadInfo(self.game_info, c.LEVEL)

    def setup_background(self) -> None:
        """Set up background image and rect."""
        raise NotImplementedError("Subclasses must implement setup_background")

    def setup_ground(self) -> None:
        """Set up ground collision rectangles."""
        raise NotImplementedError("Subclasses must implement setup_ground")

    def setup_pipes(self) -> None:
        """Set up pipe obstacles."""
        pass

    def setup_steps(self) -> None:
        """Set up step obstacles."""
        pass

    def setup_bricks(self) -> None:
        """Set up brick blocks."""
        pass

    def setup_coin_boxes(self) -> None:
        """Set up coin blocks."""
        pass

    def setup_flag_pole(self) -> None:
        """Set up flag pole at level end."""
        pass

    def setup_enemies(self) -> None:
        """Set up enemy sprites."""
        raise NotImplementedError("Subclasses must implement setup_enemies")

    def setup_mario(self) -> None:
        """Set up Mario player sprite."""
        self.mario = mario_module.Mario()

    def setup_checkpoints(self) -> None:
        """Set up checkpoint triggers."""
        pass

    def setup_spritegroups(self) -> None:
        """Initialize all sprite groups."""
        self.ground_group = pg.sprite.Group()
        self.pipe_group = pg.sprite.Group()
        self.step_group = pg.sprite.Group()
        self.brick_group = pg.sprite.Group()
        self.coin_box_group = pg.sprite.Group()
        self.flag_pole_group = pg.sprite.Group()
        self.enemy_group = pg.sprite.Group()
        self.checkpoint_group = pg.sprite.Group()
        self.flag_group = pg.sprite.Group()
        self.coin_group = pg.sprite.Group()
        self.powerup_group = pg.sprite.Group()
        self.fire_group = pg.sprite.Group()

    def update(self, surface: pg.Surface, keys: tuple, current_time: float) -> None:
        """Update level state."""
        self.current_time = current_time

        if self.state == c.FROZEN:
            self.draw(surface)
            return

        self.update_entities(current_time)
        self.check_collisions()
        self.check_state_triggers()

        if self.mario and not self.mario.dead:
            self.update_viewport()

        self.draw(surface)

    def update_entities(self, current_time: float) -> None:
        """Update all game entities."""
        if self.mario:
            self.mario.update((), current_time)

        if self.enemy_group:
            self.enemy_group.update(current_time)

        if self.powerup_group:
            self.powerup_group.update(current_time)

        if self.fire_group:
            self.fire_group.update(current_time)

        if self.brick_group:
            self.brick_group.update()

        if self.coin_box_group:
            self.coin_box_group.update()

    def check_collisions(self) -> None:
        """Check all collisions."""
        raise NotImplementedError("Subclasses must implement check_collisions")

    def check_state_triggers(self) -> None:
        """Check for state transition triggers."""
        if self.mario and self.mario.dead:
            self.state = c.FROZEN
            self.game_info[c.MARIO_DEAD] = True

    def update_viewport(self) -> None:
        """Update camera viewport based on Mario position."""
        if not self.mario or not self.viewport:
            return

        _ = self.game_info  # game_info reserved for future use
        level_rect = self.level_rect

        if self.mario.rect.right > self.viewport.centerx:
            self.viewport.centerx = self.mario.rect.centerx
            if self.mario.rect.right > level_rect.right:
                self.viewport.right = level_rect.right
            else:
                self.viewport.right = (
                    level_rect.right if self.viewport.right > level_rect.right else self.viewport.right
                )

        if self.mario.rect.left < self.viewport.x:
            self.mario.rect.left = self.viewport.x

        if self.viewport.x < 0:
            self.viewport.x = 0
        elif self.viewport.right > level_rect.right:
            self.viewport.right = level_rect.right

    def draw(self, surface: pg.Surface) -> None:
        """Render the level."""
        if self.level is None or self.background is None:
            return

        self.level.blit(self.background, self.back_rect, self.viewport)

        # Draw all sprite groups
        for group in [
            self.ground_group,
            self.pipe_group,
            self.step_group,
            self.brick_group,
            self.coin_box_group,
            self.flag_pole_group,
            self.enemy_group,
            self.flag_group,
            self.powerup_group,
            self.coin_group,
            self.fire_group,
        ]:
            if group:
                group.draw(self.level)

        if self.mario:
            self.mario.draw(self.level)

        if self.overhead_info_display:
            self.overhead_info_display.draw(self.level)

        surface.blit(self.level, (0, 0), self.viewport)

    def get_event(self, event: pg.event.Event) -> None:
        """Handle pygame events."""
        if self.mario:
            self.mario.get_event(event)
