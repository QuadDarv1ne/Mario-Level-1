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
        self.background: pg.Surface = None  # type: ignore[assignment]
        self.background_rect: pg.Rect = None  # type: ignore[assignment]
        self.viewport: pg.Rect = None  # type: ignore[assignment]
        self.image_dict: Dict[str, Tuple[pg.Surface, pg.Rect]] = {}
        self.mario: Optional[mario.Mario] = None
        self.cursor: Optional[pg.sprite.Sprite] = None
        self.menu_options = ["PLAY", "LEVEL SELECT", "SETTINGS", "EXIT"]
        self.selected_option = 0
        self.animation_timer = 0
        self.title_y_offset = 0
        self.setup_background()
        self.setup_mario()
        self.setup_cursor()

    def setup_cursor(self) -> None:
        """Creates the mushroom cursor to select menu option"""
        self.cursor = pg.sprite.Sprite()
        dest = (220, 320)
        image, rect = self.get_image(24, 160, 8, 8, dest, setup.GFX["item_objects"])
        self.cursor.image = image
        self.cursor.rect = rect
        self.cursor.state = 0  # type: ignore[attr-defined]

    def setup_mario(self) -> None:
        """Places Mario at the beginning of the level"""
        self.mario = mario.Mario()
        if self.mario.rect:
            self.mario.rect.x = 110
            self.mario.rect.bottom = c.GROUND_HEIGHT

    def setup_background(self) -> None:
        """Setup the background image to blit"""
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
        title_screen = setup.GFX.get("title_screen")
        if title_screen:
            self.image_dict["GAME_NAME_BOX"] = self.get_image(1, 60, 176, 88, (170, 80), title_screen)

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
        
        # Animate title
        self.animation_timer += 1
        self.title_y_offset = int(5 * pg.math.Vector2(0, 1).rotate(self.animation_timer * 2).y)

        # Draw background
        surface.blit(self.background, self.viewport, self.viewport)
        
        # Draw semi-transparent overlay for better text visibility
        overlay = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Draw title with animation
        game_box = self.image_dict["GAME_NAME_BOX"]
        title_rect = game_box[1].copy()
        title_rect.y += self.title_y_offset
        surface.blit(game_box[0], title_rect)

        # Draw version info
        self._draw_text(surface, "v2.7.0 - Enhanced Edition", 400, 180, c.YELLOW, 20)

        # Draw menu options with enhanced styling
        menu_start_y = 320
        for i, option in enumerate(self.menu_options):
            y_pos = menu_start_y + (i * 50)
            
            # Highlight selected option
            if i == self.selected_option:
                color = c.YELLOW
                size = 35
                # Draw selection box
                box_rect = pg.Rect(250, y_pos - 20, 300, 40)
                pg.draw.rect(surface, c.GOLD, box_rect, 3, border_radius=5)
            else:
                color = c.WHITE
                size = 30
            
            self._draw_text(surface, option, 400, y_pos, color, size)

        # Draw instructions
        self._draw_text(surface, "↑↓ to select  |  ENTER to confirm  |  ESC to exit", 400, 550, c.WHITE, 18)

        # Draw Mario
        if self.mario and self.mario.image and self.mario.rect:
            surface.blit(self.mario.image, self.mario.rect)
            
        # Draw cursor
        if self.cursor and self.cursor.image and hasattr(self.cursor, "rect") and self.cursor.rect:
            surface.blit(self.cursor.image, self.cursor.rect)
            
        self.overhead_info.draw(surface)

    def _draw_text(
        self, surface: pg.Surface, text: str, x: int, y: int, color: Tuple[int, int, int], size: int = 30
    ) -> None:
        """Draw text on surface with shadow for better visibility"""
        font = pg.font.Font(None, size)
        
        # Draw shadow
        shadow_surface = font.render(text, True, c.BLACK)
        shadow_rect = shadow_surface.get_rect(center=(x + 2, y + 2))
        surface.blit(shadow_surface, shadow_rect)
        
        # Draw text
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)

    def update_cursor(self, keys: Tuple[bool, ...]) -> None:
        """Update the position of the cursor"""
        # Handle navigation
        if keys[pg.K_DOWN]:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            if self.cursor and self.cursor.rect:
                self.cursor.rect.y = 313 + (self.selected_option * 50)
                
        elif keys[pg.K_UP]:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            if self.cursor and self.cursor.rect:
                self.cursor.rect.y = 313 + (self.selected_option * 50)

        # Handle selection
        if keys[pg.K_RETURN] or keys[pg.K_a] or keys[pg.K_s]:
            if self.selected_option == 0:  # PLAY
                self.reset_game_info()
                self.next = c.LOAD_SCREEN
                self.done = True
            elif self.selected_option == 1:  # LEVEL SELECT
                self.next = c.LEVEL_SELECT
                self.done = True
            elif self.selected_option == 2:  # SETTINGS
                # TODO: Implement settings menu
                pass
            elif self.selected_option == 3:  # EXIT
                pg.quit()
                import sys
                sys.exit()
                
        # Handle ESC to exit
        if keys[pg.K_ESCAPE]:
            pg.quit()
            import sys
            sys.exit()

    def reset_game_info(self) -> None:
        """Resets the game info in case of a Game Over and restart"""
        self.game_info[c.COIN_TOTAL] = 0
        self.game_info[c.SCORE] = 0
        self.game_info[c.LIVES] = 3
        self.game_info[c.CURRENT_TIME] = 0.0
        self.game_info[c.LEVEL_STATE] = None

        self.persist = self.game_info
