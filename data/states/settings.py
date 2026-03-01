"""Settings menu state for Super Mario Bros."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import pygame as pg

from .. import setup, tools
from .. import constants as c
from ..components import info


class Settings(tools._State):
    """Settings menu state"""

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
        }
        self.startup(0.0, persist)

    def startup(self, current_time: float, persist: Dict[str, Any]) -> None:
        """Called every time the game's state becomes this one"""
        self.next = c.MAIN_MENU
        self.persist = persist
        self.game_info = persist
        self.overhead_info = info.OverheadInfo(self.game_info, c.MAIN_MENU)

        self.background: pg.Surface = None  # type: ignore[assignment]
        self.selected_option = 0
        self.input_timer = 0
        self.input_delay = 200
        
        # Settings options
        self.settings = {
            "music_volume": 70,
            "sfx_volume": 80,
            "fullscreen": False,
            "show_fps": False,
        }
        
        self.menu_options = ["Music Volume", "SFX Volume", "Fullscreen", "Show FPS", "Back"]
        self.setup_background()

    def setup_background(self) -> None:
        """Setup the background"""
        self.background = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        self.background.fill(c.BLACK)

    def update(self, surface: pg.Surface, keys: Tuple[bool, ...], current_time: float) -> None:
        """Updates the state every refresh"""
        self.current_time = current_time
        self.game_info[c.CURRENT_TIME] = self.current_time
        self.update_cursor(keys)
        self.overhead_info.update(self.game_info)

        # Draw background
        surface.blit(self.background, (0, 0))
        
        # Draw gradient overlay
        for i in range(c.SCREEN_HEIGHT):
            alpha = int(100 * (1 - i / c.SCREEN_HEIGHT))
            color = (0, 50, 100, alpha)
            pg.draw.line(surface, color[:3], (0, i), (c.SCREEN_WIDTH, i))

        # Draw title
        self._draw_text(surface, "SETTINGS", 400, 80, c.YELLOW, 50)
        
        # Draw settings options
        menu_start_y = 200
        for i, option in enumerate(self.menu_options):
            y_pos = menu_start_y + (i * 60)
            
            # Get value for display
            if option == "Music Volume":
                value = f"{self.settings['music_volume']}%"
            elif option == "SFX Volume":
                value = f"{self.settings['sfx_volume']}%"
            elif option == "Fullscreen":
                value = "ON" if self.settings['fullscreen'] else "OFF"
            elif option == "Show FPS":
                value = "ON" if self.settings['show_fps'] else "OFF"
            else:
                value = ""
            
            # Highlight selected option
            if i == self.selected_option:
                color = c.YELLOW
                size = 35
                # Draw selection box
                box_rect = pg.Rect(150, y_pos - 20, 500, 40)
                pg.draw.rect(surface, c.GOLD, box_rect, 3, border_radius=5)
            else:
                color = c.WHITE
                size = 30
            
            # Draw option name
            self._draw_text(surface, option, 250, y_pos, color, size)
            
            # Draw value
            if value:
                self._draw_text(surface, value, 550, y_pos, color, size)

        # Draw instructions
        self._draw_text(surface, "↑↓ to select  |  ←→ to change  |  ESC to back", 400, 550, c.WHITE, 18)

        self.overhead_info.draw(surface)

    def _draw_text(
        self, surface: pg.Surface, text: str, x: int, y: int, color: Tuple[int, int, int], size: int = 30
    ) -> None:
        """Draw text on surface with shadow"""
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
        current_time = pg.time.get_ticks()
        can_input = current_time - self.input_timer > self.input_delay
        
        # Navigation
        if can_input and keys[pg.K_DOWN]:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            self.input_timer = current_time
                
        elif can_input and keys[pg.K_UP]:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            self.input_timer = current_time

        # Change values
        if can_input and keys[pg.K_RIGHT]:
            self._change_setting(1)
            self.input_timer = current_time
            
        elif can_input and keys[pg.K_LEFT]:
            self._change_setting(-1)
            self.input_timer = current_time

        # Handle selection
        if keys[pg.K_RETURN] or keys[pg.K_a] or keys[pg.K_s]:
            if self.selected_option == len(self.menu_options) - 1:  # Back
                self.done = True
                
        # Handle ESC to go back
        if keys[pg.K_ESCAPE]:
            self.done = True

    def _change_setting(self, direction: int) -> None:
        """Change the selected setting"""
        option = self.menu_options[self.selected_option]
        
        if option == "Music Volume":
            self.settings['music_volume'] = max(0, min(100, self.settings['music_volume'] + direction * 10))
            pg.mixer.music.set_volume(self.settings['music_volume'] / 100)
            
        elif option == "SFX Volume":
            self.settings['sfx_volume'] = max(0, min(100, self.settings['sfx_volume'] + direction * 10))
            # Update all sound effects volume
            for sound in setup.SFX.values():
                if sound:
                    sound.set_volume(self.settings['sfx_volume'] / 100)
                    
        elif option == "Fullscreen":
            self.settings['fullscreen'] = not self.settings['fullscreen']
            if self.settings['fullscreen']:
                setup.SCREEN = pg.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pg.FULLSCREEN)
            else:
                setup.SCREEN = pg.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
                
        elif option == "Show FPS":
            self.settings['show_fps'] = not self.settings['show_fps']
