"""
This module initializes the display and creates dictionaries of resources.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import pygame as pg

from . import constants as c
from . import tools

# Configure module logger
logger = logging.getLogger(__name__)

ORIGINAL_CAPTION: str = c.ORIGINAL_CAPTION

# Global resources
FONTS: Dict[str, str] = {}
MUSIC: Dict[str, str] = {}
GFX: Dict[str, pg.Surface] = {}
SFX: Dict[str, pg.mixer.Sound] = {}

# Display surfaces
SCREEN: Optional[pg.Surface] = None
SCREEN_RECT: Optional[pg.Rect] = None


def initialize_display() -> None:
    """
    Initialize pygame display.

    Sets up the main game window with centered positioning.
    """
    global SCREEN, SCREEN_RECT

    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pg.init()
    pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])
    pg.display.set_caption(ORIGINAL_CAPTION)
    SCREEN = pg.display.set_mode(c.SCREEN_SIZE)
    SCREEN_RECT = SCREEN.get_rect()
    logger.info(f"Display initialized: {c.SCREEN_SIZE}")


def load_resources() -> None:
    """
    Load all game resources (graphics, sound, music, fonts).

    Handles missing resource directories gracefully.
    """
    global FONTS, MUSIC, GFX, SFX

    resources_dir = "resources"

    # Load fonts
    fonts_dir = os.path.join(resources_dir, "fonts")
    if os.path.exists(fonts_dir):
        FONTS = tools.load_all_fonts(fonts_dir)
        logger.info(f"Loaded {len(FONTS)} fonts")
    else:
        logger.warning(f"Fonts directory not found: {fonts_dir}")

    # Load music
    music_dir = os.path.join(resources_dir, "music")
    if os.path.exists(music_dir):
        MUSIC = tools.load_all_music(music_dir)
        logger.info(f"Loaded {len(MUSIC)} music tracks")
    else:
        logger.warning(f"Music directory not found: {music_dir}")

    # Load graphics
    graphics_dir = os.path.join(resources_dir, "graphics")
    if os.path.exists(graphics_dir):
        GFX = tools.load_all_gfx(graphics_dir)
        logger.info(f"Loaded {len(GFX)} graphics")
    else:
        logger.warning(f"Graphics directory not found: {graphics_dir}")

    # Load sound effects
    sound_dir = os.path.join(resources_dir, "sound")
    if os.path.exists(sound_dir):
        SFX = tools.load_all_sfx(sound_dir)
        logger.info(f"Loaded {len(SFX)} sound effects")
    else:
        logger.warning(f"Sound directory not found: {sound_dir}")


def initialize() -> None:
    """
    Initialize the entire setup (display + resources).

    Call this once at game startup.
    """
    initialize_display()
    load_resources()


# =============================================================================
# Factory functions for game states
# =============================================================================


def create_main_menu() -> Optional[Any]:
    """Create main menu state."""
    try:
        from .states import main_menu

        return main_menu.Menu()
    except Exception as e:
        logger.error(f"Failed to create main menu: {e}")
        return None


def create_level_select() -> Optional[Any]:
    """Create level select state."""
    try:
        from .states import level_select

        return level_select.LevelSelect()
    except Exception as e:
        logger.error(f"Failed to create level select: {e}")
        return None


def create_load_screen() -> Optional[Any]:
    """Create load screen state."""
    try:
        from .states import load_screen

        return load_screen.LoadScreen()
    except Exception as e:
        logger.error(f"Failed to create load screen: {e}")
        return None


def create_timeout_screen() -> Optional[Any]:
    """Create timeout screen state."""
    try:
        from .states import load_screen

        return load_screen.TimeOut()
    except Exception as e:
        logger.error(f"Failed to create timeout screen: {e}")
        return None


def create_game_over() -> Optional[Any]:
    """Create game over state."""
    try:
        from .states import load_screen

        return load_screen.GameOver()
    except Exception as e:
        logger.error(f"Failed to create game over: {e}")
        return None


def create_level1() -> Optional[Any]:
    """Create level 1 state."""
    try:
        from .states import level1

        return level1.Level1()
    except Exception as e:
        logger.error(f"Failed to create level 1: {e}")
        return None


def create_level2() -> Optional[Any]:
    """Create level 2 state."""
    try:
        from .states import level2

        return level2.Level2()
    except Exception as e:
        logger.error(f"Failed to create level 2: {e}")
        return None


def create_level3() -> Optional[Any]:
    """Create level 3 state."""
    try:
        from .states import level3

        return level3.Level3()
    except Exception as e:
        logger.error(f"Failed to create level 3: {e}")
        return None


def create_level4() -> Optional[Any]:
    """Create level 4 state."""
    try:
        from .states import level4

        return level4.Level4()
    except Exception as e:
        logger.error(f"Failed to create level 4: {e}")
        return None


def create_level5() -> Optional[Any]:
    """Create level 5 state."""
    try:
        from .states import level5

        return level5.Level5()
    except Exception as e:
        logger.error(f"Failed to create level 5: {e}")
        return None


# Initialize on module import for backward compatibility
try:
    initialize()
except Exception as e:
    logger.error(f"Setup initialization failed: {e}")


# Minimal fallback resources for tests/environments without assets
try:
    if "smb_enemies_sheet" not in GFX:
        # Provide a dummy surface to prevent KeyError in tests
        GFX["smb_enemies_sheet"] = pg.Surface((512, 512))
except Exception:
    # If pygame isn't fully functional, skip creating surfaces
    pass
