"""Level 8 state for Super Mario Bros - World 2-4 (Castle)."""

from __future__ import annotations

from .level5 import Level5


class Level8(Level5):
    """Level 8 - World 2-4 (Castle with fake Bowser)"""

    def __init__ (self) -> None:
        super().__init__()
        self.level_file = "data/levels/level_2_4.json"
