"""Main menu state for Super Mario Bros."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import pygame as pg

from .. import setup, tools
from .. import constants as c
from ..components import info, mario


class Menu(tools._State):
    def __init__(self) -> None:
        """Initializes the state"""
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
        }
        self.startup(0.0, persist)

    def startup(self, current_time: float, persist: Dict[str, Any]) -> None:
        """Called every time the game's state becomes this one.  Initializes
        certain values"""
        self.next = c.LOAD_SCREEN
        self.persist = persist
        self.game_info = persist
        self.overhead_info = info.OverheadInfo(self.game_info, c.MAIN_MENU)

        self.sprite_sheet = setup.GFX["title_screen"]
        self.background: Optional[pg.Surface] = None
        self.background_rect: Optional[pg.Rect] = None
        self.viewport: Optional[pg.Rect] = None
        self.image_dict: Dict[str, Tuple[pg.Surface, pg.Rect]] = {}
        self.mario: Optional[mario.Mario] = None
        self.cursor: Optional[pg.sprite.Sprite] = None
        self.setup_background()
        self.setup_mario()
        self.setup_cursor()

    def setup_cursor(self) -> None:
        """Creates the mushroom cursor to select 1 or 2 player game"""
        self.cursor = pg.sprite.Sprite()
        dest = (220, 358)
        image, rect = self.get_image(24, 160, 8, 8, dest, setup.GFX["item_objects"])
        self.cursor.image = image
        self.cursor.rect = rect
        self.cursor.state = c.PLAYER1  # type: ignore[attr-defined]

    def setup_mario(self) -> None:
        """Places Mario at the beginning of the level"""
        self.mario = mario.Mario()
        if self.mario.rect:
            self.mario.rect.x = 110
            self.mario.rect.bottom = c.GROUND_HEIGHT

    def setup_background(self) -> None:
        """Setup the background image to blit"""
        self.background = setup.GFX["level_1"]
        self.background_rect = self.background.get_rect()
        self.background = pg.transform.scale(
            self.background,
            (
                int(self.background_rect.width * c.BACKGROUND_MULTIPLIER),
                int(self.background_rect.height * c.BACKGROUND_MULTIPLIER),
            ),
        )
        self.viewport = setup.SCREEN.get_rect(bottom=setup.SCREEN_RECT.bottom)

        self.image_dict = {}
        self.image_dict["GAME_NAME_BOX"] = self.get_image(1, 60, 176, 88, (170, 100), setup.GFX["title_screen"])

    def get_image(
        self, x: int, y: int, width: int, height: int, dest: Tuple[int, int], sprite_sheet: pg.Surface
    ) -> Tuple[pg.Surface, pg.Rect]:
        """Returns images and rects to blit onto the screen"""
        image = pg.Surface([width, height])
        rect = image.get_rect()

        image.blit(sprite_sheet, (0, 0), (x, y, width, height))
        if sprite_sheet == setup.GFX["title_screen"]:
            image.set_colorkey((255, 0, 220))
            image = pg.transform.scale(
                image, (int(rect.width * c.SIZE_MULTIPLIER), int(rect.height * c.SIZE_MULTIPLIER))
            )
        else:
            image.set_colorkey(c.BLACK)
            image = pg.transform.scale(image, (int(rect.width * 3), int(rect.height * 3)))

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

        surface.blit(self.background, self.viewport, self.viewport)
        game_box = self.image_dict["GAME_NAME_BOX"]
        if game_box:
            surface.blit(game_box[0], game_box[1])
        if self.mario.image and self.mario.rect:
            surface.blit(self.mario.image, self.mario.rect)
        if self.cursor.image and self.cursor.rect:
            surface.blit(self.cursor.image, self.cursor.rect)
        self.overhead_info.draw(surface)

    def update_cursor(self, keys: Tuple[bool, ...]) -> None:
        """Update the position of the cursor"""
        input_list = [pg.K_RETURN, pg.K_a, pg.K_s]

        if self.cursor.state == c.PLAYER1:
            self.cursor.rect.y = 358
            if keys[pg.K_DOWN]:
                self.cursor.state = c.PLAYER2
            for input in input_list:
                if keys[input]:
                    self.reset_game_info()
                    self.done = True
        elif self.cursor.state == c.PLAYER2:
            self.cursor.rect.y = 403
            if keys[pg.K_UP]:
                self.cursor.state = c.PLAYER1

    def reset_game_info(self) -> None:
        """Resets the game info in case of a Game Over and restart"""
        self.game_info[c.COIN_TOTAL] = 0
        self.game_info[c.SCORE] = 0
        self.game_info[c.LIVES] = 3
        self.game_info[c.CURRENT_TIME] = 0.0
        self.game_info[c.LEVEL_STATE] = None

        self.persist = self.game_info
