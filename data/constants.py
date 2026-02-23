"""
Game constants and configuration values.

This module is deprecated. Import from data.constants instead.
For better organization, use submodules:
    - from data.constants import colors
    - from data.constants import physics
    - from data.constants import states
    - from data.constants import items
    - from data.constants import screen
"""
from __future__ import annotations

import warnings

warnings.warn(
    "Importing from data.constants directly is deprecated. "
    "Use data.constants module (it now re-exports all constants).",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new constants package
from .constants import *  # noqa: F401, F403, E402
