"""
Save/Load system for game progress.
Supports saving game state to JSON file.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from . import constants as c


SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saves')
SAVE_FILE = os.path.join(SAVE_DIR, 'save_data.json')


class GameSave:
    """Container for save game data."""

    def __init__(self) -> None:
        self.score: int = 0
        self.coin_total: int = 0
        self.lives: int = 3
        self.top_score: int = 0
        self.current_level: str = c.LEVEL1
        self.timestamp: str = ''
        self.play_time: int = 0  # Total play time in seconds

        # Level-specific progress
        self.levels_completed: list[str] = []
        self.enemies_defeated: int = 0
        self.blocks_broken: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert save data to dictionary."""
        return {
            'score': self.score,
            'coin_total': self.coin_total,
            'lives': self.lives,
            'top_score': self.top_score,
            'current_level': self.current_level,
            'timestamp': self.timestamp,
            'play_time': self.play_time,
            'levels_completed': self.levels_completed,
            'enemies_defeated': self.enemies_defeated,
            'blocks_broken': self.blocks_broken
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GameSave:
        """Create GameSave from dictionary."""
        save = cls()
        save.score = data.get('score', 0)
        save.coin_total = data.get('coin_total', 0)
        save.lives = data.get('lives', 3)
        save.top_score = data.get('top_score', 0)
        save.current_level = data.get('current_level', c.LEVEL1)
        save.timestamp = data.get('timestamp', '')
        save.play_time = data.get('play_time', 0)
        save.levels_completed = data.get('levels_completed', [])
        save.enemies_defeated = data.get('enemies_defeated', 0)
        save.blocks_broken = data.get('blocks_broken', 0)
        return save


def ensure_save_dir() -> None:
    """Ensure save directory exists."""
    os.makedirs(SAVE_DIR, exist_ok=True)


def save_game(game_save: GameSave) -> bool:
    """
    Save game progress to file.

    Args:
        game_save: GameSave object containing progress data

    Returns:
        True if save was successful, False otherwise
    """
    try:
        ensure_save_dir()
        game_save.timestamp = datetime.now().isoformat()

        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(game_save.to_dict(), f, indent=2, ensure_ascii=False)

        return True
    except (IOError, OSError, json.JSONEncodeError) as e:
        print(f"Save error: {e}")
        return False


def load_game() -> GameSave | None:
    """
    Load game progress from file.

    Returns:
        GameSave object if load successful, None otherwise
    """
    if not os.path.exists(SAVE_FILE):
        return None

    try:
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return GameSave.from_dict(data)
    except (IOError, OSError, json.JSONDecodeError) as e:
        print(f"Load error: {e}")
        return None


def delete_save() -> bool:
    """
    Delete save file.

    Returns:
        True if deletion successful or file didn't exist, False otherwise
    """
    try:
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        return True
    except OSError as e:
        print(f"Delete error: {e}")
        return False


def save_exists() -> bool:
    """Check if a save file exists."""
    return os.path.exists(SAVE_FILE)


def get_save_info() -> dict[str, Any] | None:
    """
    Get basic info about save file without loading full data.

    Returns:
        Dictionary with timestamp, score, level or None if no save exists
    """
    if not os.path.exists(SAVE_FILE):
        return None

    try:
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return {
            'timestamp': data.get('timestamp', 'Unknown'),
            'score': data.get('score', 0),
            'level': data.get('current_level', 'Unknown'),
            'play_time': data.get('play_time', 0)
        }
    except (IOError, OSError, json.JSONDecodeError):
        return None


def create_save_from_game_info(game_info: dict[str, Any]) -> GameSave:
    """
    Create a GameSave object from game_info dictionary.

    Args:
        game_info: The game_info dictionary from the game state

    Returns:
        GameSave object with current game state
    """
    save = GameSave()
    save.score = game_info.get(c.SCORE, 0)
    save.coin_total = game_info.get(c.COIN_TOTAL, 0)
    save.lives = game_info.get(c.LIVES, 3)
    save.top_score = game_info.get(c.TOP_SCORE, 0)
    save.current_level = game_info.get(c.LEVEL_STATE, c.LEVEL1)
    return save


def update_game_info_from_save(game_info: dict[str, Any], save: GameSave) -> None:
    """
    Update game_info dictionary with saved data.

    Args:
        game_info: The game_info dictionary to update
        save: GameSave object with saved data
    """
    game_info[c.SCORE] = save.score
    game_info[c.COIN_TOTAL] = save.coin_total
    game_info[c.LIVES] = save.lives
    game_info[c.TOP_SCORE] = save.top_score
