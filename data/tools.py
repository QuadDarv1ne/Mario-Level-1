"""
Core tools and base classes for the game.

This module is deprecated. Import from data.tools instead.
For better organization, use submodules:
    - from data.tools.controllers import Control
    - from data.tools.states import _State
    - from data.tools.resources import load_all_gfx, load_all_music, ...
    - from data.tools.keybindings import keybinding, KeyBindings
"""
from __future__ import annotations

import warnings

warnings.warn(
    "Importing from data.tools directly is deprecated. "
    "Use data.tools module (it now re-exports all components).",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new tools package
from .tools import *  # noqa: F401, F403, E402
