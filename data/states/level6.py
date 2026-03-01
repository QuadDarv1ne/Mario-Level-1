"""Level 6 state for Super Mario Bros - World 2-2 (Underwater)."""

from __future__ import annotations

from .level5 import Level5


class Level6(Level5):
    """Level 6 - World 2-2 (Underwater level)"""

    def __init__(self) -> None:
        super().__init__()
        self.level_file = "data/levels/level_2_2.json"
