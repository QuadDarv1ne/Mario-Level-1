"""
This module initializes the display and creates dictionaries of resources.
"""

from __future__ import annotations

import os
from typing import Dict

import pygame as pg

from . import tools
from . import constants as c

ORIGINAL_CAPTION: str = c.ORIGINAL_CAPTION

os.environ["SDL_VIDEO_CENTERED"] = "1"
pg.init()
pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])
pg.display.set_caption(ORIGINAL_CAPTION)
SCREEN: pg.Surface = pg.display.set_mode(c.SCREEN_SIZE)
SCREEN_RECT: pg.Rect = SCREEN.get_rect()

FONTS: Dict[str, str] = tools.load_all_fonts(os.path.join("resources", "fonts"))
MUSIC: Dict[str, str] = tools.load_all_music(os.path.join("resources", "music"))
GFX: Dict[str, pg.Surface] = tools.load_all_gfx(os.path.join("resources", "graphics"))
SFX: Dict[str, pg.mixer.Sound] = tools.load_all_sfx(os.path.join("resources", "sound"))
