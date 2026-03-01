"""Level selection menu state for Super Mario Bros."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, List

import pygame as pg

from .. import setup, tools
from .. import constants as c
from ..components import info, mario


class LevelSelect(tools._State):
    """Level selection menu state"""

    def __init__(self) -> None:
        tools._State.__init__(self)
        persist: Dict[str, Any] = {
            c.COIN_TOTAL: 0,
            c.SCORE: 0,
            c.LIVES: 3,
            c.TOP_SCORE: 0,
            c.CURRENT_TIME: 0.0,
            c.LEVEL_STATE: None,
            c.CAMERA_START_X: 0,
            c.MARIO_DEAD: False,
            c.CURRENT_LEVEL: c.LEVEL1,
        }
        self.startup(0.0, persist)

    def startup(self, current_time: float, persist: Dict[str, Any]) -> None:
        """Called every time the game's state becomes this one"""
        self.next = c.LOAD_SCREEN
        self.persist = persist
        self.game_info = persist
        self.overhead_info = info.OverheadInfo(self.game_info, c.MAIN_MENU)

        self.sprite_sheet = setup.GFX.get("title_screen")
        self.background: pg.Surface = None  # type: ignore[assignment]
        self.background_rect: pg.Rect = None  # type: ignore[assignment]
        self.viewport: pg.Rect = None  # type: ignore[assignment]
        self.image_dict: Dict[str, Tuple[pg.Surface, pg.Rect]] = {}
        self.mario: Optional[mario.Mario] = None
        self.cursor: Optional[pg.sprite.Sprite] = None
        self.selected_level: int = 0
        self.level_names: List[str] = [
            "LEVEL 1-1",
            "LEVEL 1-2", 
            "LEVEL 1-3",
            "LEVEL 1-4",
            "LEVEL 2-1",
        ]
        self.level_constants: List[str] = [
            c.LEVEL1,
            c.LEVEL2,
            c.LEVEL3,
            c.LEVEL4,
            c.LEVEL5,
        ]
        self.setup_background()
        self.setup_mario()
        self.setup_cursor()

    def setup_cursor(self) -> None:
        """Creates the cursor to select level"""
        self.cursor = pg.sprite.Sprite()
        image = pg.Surface([16, 16])
        image.fill(c.RED)
        rect = image.get_rect()
        self.cursor.image = image
        self.cursor.rect = rect
        self.cursor.state = c.PLAYER1  # type: ignore[attr-defined]
        self._update_cursor_position()

    def _update_cursor_position(self) -> None:
        """Updates cursor position based on selected level"""
        if self.cursor and self.cursor.rect:
            self.cursor.rect.x = 220
            self.cursor.rect.y = 280 + (self.selected_level * 40)

    def setup_mario(self) -> None:
        """Places Mario at the side"""
        self.mario = mario.Mario()
        if self.mario and self.mario.rect:
            self.mario.rect.x = 500
            self.mario.rect.bottom = c.GROUND_HEIGHT - 50

    def setup_background(self) -> None:
        """Setup the background image"""
        level_1_img = setup.GFX.get("level_1")
        if level_1_img is None:
            level_1_img = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        self.background = level_1_img
        self.background_rect = self.background.get_rect()
        scaled_background = pg.transform.scale(
            self.background,
            (
                int(self.background_rect.width * c.BACKGROUND_MULTIPLIER),
                int(self.background_rect.height * c.BACKGROUND_MULTIPLIER),
            ),
        )
        if scaled_background:
            self.background = scaled_background
            self.background_rect = self.background.get_rect()
        screen_rect = setup.SCREEN.get_rect(bottom=setup.SCREEN_RECT.bottom)
        if screen_rect:
            self.viewport = screen_rect

        self.image_dict = {}
        self.image_dict["GAME_NAME_BOX"] = self.get_image(1, 60, 176, 88, (170, 100), setup.GFX.get("title_screen"))

    def get_image(
        self, x: int, y: int, width: int, height: int, dest: Tuple[int, int], sprite_sheet: Optional[pg.Surface]
    ) -> Tuple[pg.Surface, pg.Rect]:
        """Returns images and rects to blit onto the screen"""
        image = pg.Surface([width, height])
        rect = image.get_rect()

        if sprite_sheet:
            image.blit(sprite_sheet, (0, 0), (x, y, width, height))
            image.set_colorkey((255, 0, 220))
            image = pg.transform.scale(
                image, (int(rect.width * c.SIZE_MULTIPLIER), int(rect.height * c.SIZE_MULTIPLIER))
            )
        else:
            image.fill(c.WHITE)

        rect = image.get_rect()
        rect.x = dest[0]
        rect.y = dest[1]
        return (image, rect)

    def update(self, surface: pg.Surface, keys: Tuple[bool, ...], current_time: float) -> None:
        """Updates the state every refresh"""
        self.current_time = current_time
        self.game_info[c.CURRENT_TIME] = self.current_time
        self.update_cursor(keys)
        self.overhead_info.update(self.game_info)

        surface.fill(c.BLACK)
        if self.background and self.background_rect and self.viewport:
            surface.blit(self.background, self.viewport, self.viewport)

        # Draw title
        self._draw_text(surface, "SELECT LEVEL", 350, 150, c.WHITE, 40)

        # Draw level options
        for i, level_name in enumerate(self.level_names):
            color = c.YELLOW if i == self.selected_level else c.WHITE
            self._draw_text(surface, level_name, 350, 280 + (i * 40), color, 30)

        # Draw cursor
        if self.cursor and self.cursor.image and hasattr(self.cursor, "rect") and self.cursor.rect:
            surface.blit(self.cursor.image, self.cursor.rect)

        # Draw Mario
        if self.mario and self.mario.image and self.mario.rect:
            surface.blit(self.mario.image, self.mario.rect)

        # Draw instructions
        self._draw_text(surface, "UP/DOWN to select, ENTER to start", 400, 520, c.WHITE, 20)
        self._draw_text(surface, "ESC to return to main menu", 400, 550, c.WHITE, 20)

        self.overhead_info.draw(surface)

    def _draw_text(
        self, surface: pg.Surface, text: str, x: int, y: int, color: Tuple[int, int, int], size: int = 30
    ) -> None:
        """Draw text on surface"""
        font = pg.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)

    def update_cursor(self, keys: Tuple[bool, ...]) -> None:
        """Update the position of the cursor"""
        if keys[pg.K_DOWN]:
            self.selected_level = (self.selected_level + 1) % len(self.level_names)
            self._update_cursor_position()
        elif keys[pg.K_UP]:
            self.selected_level = (self.selected_level - 1) % len(self.level_names)
            self._update_cursor_position()
        elif keys[pg.K_RETURN] or keys[pg.K_a] or keys[pg.K_s]:
            self.game_info[c.CURRENT_LEVEL] = self.level_constants[self.selected_level]
            self.next = c.LOAD_SCREEN
            self.done = True
        elif keys[pg.K_ESCAPE]:
            self.next = c.MAIN_MENU
            self.done = True

    def get_event(self, event: pg.event.Event) -> None:
        """Handle events"""
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_DOWN:
                self.selected_level = (self.selected_level + 1) % len(self.level_names)
                self._update_cursor_position()
            elif event.key == pg.K_UP:
                self.selected_level = (self.selected_level - 1) % len(self.level_names)
                self._update_cursor_position()
            elif event.key in (pg.K_RETURN, pg.K_a, pg.K_s):
                self.game_info[c.CURRENT_LEVEL] = self.level_constants[self.selected_level]
                self.next = c.LOAD_SCREEN
                self.done = True
            elif event.key == pg.K_ESCAPE:
                self.next = c.MAIN_MENU
                self.done = True
