"""Error handling and validation utilities for game components."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import pygame as pg


class LevelDataValidator:
    """Validates level data loaded from JSON files."""
    
    REQUIRED_SECTIONS = [
        'ground_sections',
        'pipe_sections',
        'step_sections',
        'brick_sections',
        'coin_box_sections',
    ]
    
    @staticmethod
    def validate_level_data(data: Dict[str, Any], level_name: str) -> tuple[bool, Optional[str]]:
        """Validate level data structure.
        
        Args:
            data: Level data dictionary
            level_name: Name of the level for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, f"{level_name}: Level data must be a dictionary"
        
        # Check for required sections
        missing_sections = []
        for section in LevelDataValidator.REQUIRED_SECTIONS:
            if section not in data:
                missing_sections.append(section)
        
        if missing_sections:
            return False, f"{level_name}: Missing required sections: {', '.join(missing_sections)}"
        
        # Validate each section is a list
        for section in LevelDataValidator.REQUIRED_SECTIONS:
            if not isinstance(data[section], list):
                return False, f"{level_name}: Section '{section}' must be a list"
        
        return True, None
    
    @staticmethod
    def load_and_validate_level(level_file: str) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Load and validate level data from JSON file.
        
        Args:
            level_file: Path to level JSON file
            
        Returns:
            Tuple of (level_data, error_message)
        """
        level_path = Path(level_file)
        
        # Check if file exists
        if not level_path.exists():
            return None, f"Level file not found: {level_file}"
        
        # Try to load JSON
        try:
            with open(level_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON in {level_file}: {e}"
        except Exception as e:
            return None, f"Error loading {level_file}: {e}"
        
        # Validate structure
        is_valid, error = LevelDataValidator.validate_level_data(data, level_file)
        if not is_valid:
            return None, error
        
        return data, None


class SpriteValidator:
    """Validates sprite state and prevents common errors."""
    
    @staticmethod
    def validate_rect(sprite: pg.sprite.Sprite, sprite_name: str = "Sprite") -> bool:
        """Validate sprite has valid rect.
        
        Args:
            sprite: Sprite to validate
            sprite_name: Name for error messages
            
        Returns:
            True if valid, False otherwise
        """
        if not hasattr(sprite, 'rect'):
            print(f"Warning: {sprite_name} missing rect attribute")
            return False
        
        if sprite.rect is None:
            print(f"Warning: {sprite_name} rect is None")
            return False
        
        return True
    
    @staticmethod
    def validate_frame_index(frame_index: int, frame_list: list, sprite_name: str = "Sprite") -> int:
        """Validate and clamp frame index to valid range.
        
        Args:
            frame_index: Current frame index
            frame_list: List of frames
            sprite_name: Name for error messages
            
        Returns:
            Valid frame index (clamped to range)
        """
        if not frame_list:
            print(f"Warning: {sprite_name} has empty frame list")
            return 0
        
        if frame_index < 0:
            print(f"Warning: {sprite_name} frame_index {frame_index} < 0, clamping to 0")
            return 0
        
        if frame_index >= len(frame_list):
            print(f"Warning: {sprite_name} frame_index {frame_index} >= {len(frame_list)}, clamping")
            return len(frame_list) - 1
        
        return frame_index
    
    @staticmethod
    def safe_get_image(frame_list: list, frame_index: int, default: Optional[pg.Surface] = None) -> Optional[pg.Surface]:
        """Safely get image from frame list with bounds checking.
        
        Args:
            frame_list: List of frames
            frame_index: Index to retrieve
            default: Default surface if index invalid
            
        Returns:
            Surface or default
        """
        if not frame_list:
            return default
        
        if 0 <= frame_index < len(frame_list):
            return frame_list[frame_index]
        
        return default or (frame_list[0] if frame_list else None)


class AudioErrorHandler:
    """Handles audio loading and playback errors gracefully."""
    
    @staticmethod
    def safe_load_music(music_path: str) -> bool:
        """Safely load music file.
        
        Args:
            music_path: Path to music file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            pg.mixer.music.load(music_path)
            return True
        except pg.error as e:
            print(f"Could not load music {music_path}: {e}")
            return False
        except FileNotFoundError:
            print(f"Music file not found: {music_path}")
            return False
    
    @staticmethod
    def safe_play_music(loops: int = -1, fade_ms: int = 0) -> bool:
        """Safely play loaded music.
        
        Args:
            loops: Number of loops (-1 for infinite)
            fade_ms: Fade in duration
            
        Returns:
            True if playing, False otherwise
        """
        try:
            pg.mixer.music.play(loops, fade_ms=fade_ms)
            return True
        except pg.error as e:
            print(f"Could not play music: {e}")
            return False
    
    @staticmethod
    def safe_load_sound(sound_path: str) -> Optional[pg.mixer.Sound]:
        """Safely load sound effect.
        
        Args:
            sound_path: Path to sound file
            
        Returns:
            Sound object or None if failed
        """
        try:
            return pg.mixer.Sound(sound_path)
        except pg.error as e:
            print(f"Could not load sound {sound_path}: {e}")
            return None
        except FileNotFoundError:
            print(f"Sound file not found: {sound_path}")
            return None


class GameStateValidator:
    """Validates game state and prevents invalid transitions."""
    
    @staticmethod
    def validate_game_info(game_info: Dict[str, Any]) -> bool:
        """Validate game_info dictionary has required keys.
        
        Args:
            game_info: Game info dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ['SCORE', 'COIN_TOTAL', 'LIVES', 'CURRENT_TIME', 'LEVEL_TIME']
        
        for key in required_keys:
            if key not in game_info:
                print(f"Warning: game_info missing required key: {key}")
                return False
        
        return True
    
    @staticmethod
    def safe_get_game_value(game_info: Dict[str, Any], key: str, default: Any = 0) -> Any:
        """Safely get value from game_info with default.
        
        Args:
            game_info: Game info dictionary
            key: Key to retrieve
            default: Default value if key missing
            
        Returns:
            Value or default
        """
        return game_info.get(key, default)
