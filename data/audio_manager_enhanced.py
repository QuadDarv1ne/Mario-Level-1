"""Enhanced audio manager with caching and better error handling."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import pygame as pg

from .error_handler import AudioErrorHandler


class AudioCache:
    """Caches loaded audio files to avoid reloading."""
    
    def __init__(self) -> None:
        """Initialize audio cache."""
        self._music_cache: Dict[str, str] = {}
        self._sound_cache: Dict[str, pg.mixer.Sound] = {}
    
    def cache_music_path(self, key: str, path: str) -> None:
        """Cache music file path.
        
        Args:
            key: Cache key
            path: File path
        """
        self._music_cache[key] = path
    
    def get_music_path(self, key: str) -> Optional[str]:
        """Get cached music path.
        
        Args:
            key: Cache key
            
        Returns:
            File path or None
        """
        return self._music_cache.get(key)
    
    def cache_sound(self, key: str, sound: pg.mixer.Sound) -> None:
        """Cache sound object.
        
        Args:
            key: Cache key
            sound: Sound object
        """
        self._sound_cache[key] = sound
    
    def get_sound(self, key: str) -> Optional[pg.mixer.Sound]:
        """Get cached sound.
        
        Args:
            key: Cache key
            
        Returns:
            Sound object or None
        """
        return self._sound_cache.get(key)
    
    def clear(self) -> None:
        """Clear all caches."""
        self._music_cache.clear()
        self._sound_cache.clear()


class EnhancedAudioManager:
    """Enhanced audio manager with caching and error handling."""
    
    def __init__(self, music_dir: str = "resources/music", sound_dir: str = "resources/sound") -> None:
        """Initialize enhanced audio manager.
        
        Args:
            music_dir: Directory containing music files
            sound_dir: Directory containing sound files
        """
        self.music_dir = Path(music_dir)
        self.sound_dir = Path(sound_dir)
        self.cache = AudioCache()
        
        self.music_volume = 0.7
        self.sound_volume = 0.8
        
        self.current_music: Optional[str] = None
        self.music_paused = False
    
    def load_music(self, music_name: str, subdirs: list[str] = None) -> bool:
        """Load music file with caching.
        
        Args:
            music_name: Name of music file (with or without extension)
            subdirs: Optional subdirectories to search
            
        Returns:
            True if loaded successfully, False otherwise
        """
        # Check cache first
        cached_path = self.cache.get_music_path(music_name)
        if cached_path:
            return AudioErrorHandler.safe_load_music(cached_path)
        
        # Find music file
        music_path = self._find_audio_file(self.music_dir, music_name, subdirs)
        if not music_path:
            print(f"Music file not found: {music_name}")
            return False
        
        # Load and cache
        success = AudioErrorHandler.safe_load_music(str(music_path))
        if success:
            self.cache.cache_music_path(music_name, str(music_path))
            self.current_music = music_name
        
        return success
    
    def play_music(self, loops: int = -1, fade_ms: int = 0, start: float = 0.0) -> bool:
        """Play loaded music.
        
        Args:
            loops: Number of loops (-1 for infinite)
            fade_ms: Fade in duration
            start: Start position in seconds
            
        Returns:
            True if playing, False otherwise
        """
        success = AudioErrorHandler.safe_play_music(loops, fade_ms)
        if success:
            pg.mixer.music.set_volume(self.music_volume)
            self.music_paused = False
        return success
    
    def load_and_play_music(
        self,
        music_name: str,
        loops: int = -1,
        fade_ms: int = 1000,
        subdirs: list[str] = None,
    ) -> bool:
        """Load and play music in one call.
        
        Args:
            music_name: Name of music file
            loops: Number of loops (-1 for infinite)
            fade_ms: Fade in duration
            subdirs: Optional subdirectories to search
            
        Returns:
            True if successful, False otherwise
        """
        if self.load_music(music_name, subdirs):
            return self.play_music(loops, fade_ms)
        return False
    
    def stop_music(self, fade_ms: int = 1000) -> None:
        """Stop music with fade out.
        
        Args:
            fade_ms: Fade out duration
        """
        if pg.mixer.music.get_busy():
            pg.mixer.music.fadeout(fade_ms)
        self.current_music = None
        self.music_paused = False
    
    def pause_music(self) -> None:
        """Pause music."""
        if pg.mixer.music.get_busy() and not self.music_paused:
            pg.mixer.music.pause()
            self.music_paused = True
    
    def unpause_music(self) -> None:
        """Unpause music."""
        if self.music_paused:
            pg.mixer.music.unpause()
            self.music_paused = False
    
    def set_music_volume(self, volume: float) -> None:
        """Set music volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pg.mixer.music.set_volume(self.music_volume)
    
    def load_sound(self, sound_name: str, subdirs: list[str] = None) -> Optional[pg.mixer.Sound]:
        """Load sound effect with caching.
        
        Args:
            sound_name: Name of sound file
            subdirs: Optional subdirectories to search
            
        Returns:
            Sound object or None
        """
        # Check cache first
        cached_sound = self.cache.get_sound(sound_name)
        if cached_sound:
            return cached_sound
        
        # Find sound file
        sound_path = self._find_audio_file(self.sound_dir, sound_name, subdirs)
        if not sound_path:
            print(f"Sound file not found: {sound_name}")
            return None
        
        # Load and cache
        sound = AudioErrorHandler.safe_load_sound(str(sound_path))
        if sound:
            sound.set_volume(self.sound_volume)
            self.cache.cache_sound(sound_name, sound)
        
        return sound
    
    def play_sound(self, sound_name: str, subdirs: list[str] = None) -> bool:
        """Load and play sound effect.
        
        Args:
            sound_name: Name of sound file
            subdirs: Optional subdirectories to search
            
        Returns:
            True if played successfully, False otherwise
        """
        sound = self.load_sound(sound_name, subdirs)
        if sound:
            try:
                sound.play()
                return True
            except pg.error as e:
                print(f"Could not play sound {sound_name}: {e}")
        return False
    
    def set_sound_volume(self, volume: float) -> None:
        """Set sound effects volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.sound_volume = max(0.0, min(1.0, volume))
        
        # Update all cached sounds
        for sound in self.cache._sound_cache.values():
            sound.set_volume(self.sound_volume)
    
    def _find_audio_file(
        self,
        base_dir: Path,
        filename: str,
        subdirs: list[str] = None,
    ) -> Optional[Path]:
        """Find audio file in directory and subdirectories.
        
        Args:
            base_dir: Base directory to search
            filename: Filename to find
            subdirs: Optional subdirectories to search
            
        Returns:
            Path to file or None
        """
        # Common audio extensions
        extensions = ['.mp3', '.ogg', '.wav', '.flac']
        
        # Add extension if not present
        if not any(filename.endswith(ext) for ext in extensions):
            search_names = [filename + ext for ext in extensions]
        else:
            search_names = [filename]
        
        # Search in base directory
        for name in search_names:
            path = base_dir / name
            if path.exists():
                return path
        
        # Search in subdirectories
        if subdirs:
            for subdir in subdirs:
                for name in search_names:
                    path = base_dir / subdir / name
                    if path.exists():
                        return path
        
        # Recursive search as last resort
        for name in search_names:
            for path in base_dir.rglob(name):
                return path
        
        return None
    
    def is_music_playing(self) -> bool:
        """Check if music is currently playing.
        
        Returns:
            True if playing, False otherwise
        """
        return pg.mixer.music.get_busy() and not self.music_paused
    
    def get_music_position(self) -> float:
        """Get current music position in seconds.
        
        Returns:
            Position in seconds
        """
        return pg.mixer.music.get_pos() / 1000.0
    
    def clear_cache(self) -> None:
        """Clear audio cache."""
        self.cache.clear()


# Global instance
_enhanced_audio_manager: Optional[EnhancedAudioManager] = None


def get_enhanced_audio_manager() -> EnhancedAudioManager:
    """Get global enhanced audio manager instance.
    
    Returns:
        Enhanced audio manager instance
    """
    global _enhanced_audio_manager
    if _enhanced_audio_manager is None:
        _enhanced_audio_manager = EnhancedAudioManager()
    return _enhanced_audio_manager
