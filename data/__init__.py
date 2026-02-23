"""
Super Mario Bros Level 1 - Data Package

This package contains all game data, states, and components.
"""
__author__ = 'justinarmstrong'
__version__ = '2.5.0'

from . import level_loader
from . import constants as c
from . import tools
from . import setup
from . import achievements
from . import combo_system
from . import game_settings
from . import visual_effects
from . import optimization
from . import animation_system
from . import ui
from . import weather_system
from . import audio_manager
from . import hint_system
from . import dialogue_system
from . import screenshot
from . import debug
from . import statistics

__all__ = [
    'level_loader',
    'constants',
    'tools',
    'setup',
    'achievements',
    'combo_system',
    'game_settings',
    'visual_effects',
    'optimization',
    'animation_system',
    'ui',
    'weather_system',
    'audio_manager',
    'hint_system',
    'dialogue_system',
    'screenshot',
    'debug',
    'statistics',
]
