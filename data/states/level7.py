"""Level 7 state for Super Mario Bros - World 2-3 (Bridge)."""

from __future__ import annotations

from .level5 import Level5


class Level7(Level5):
    """Level 7 - World 2-3 (Bridge level with Cheep-Cheeps)"""

    def __init__(self) -> None:
        super().__init__()
        self.level_file = "data/levels/level_2_3.json"
