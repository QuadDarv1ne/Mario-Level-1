"""
Memory optimization utilities for reduced allocations.

Features:
- Rect pooling for reduced allocations
- Object reuse patterns
- Memory-efficient containers
"""
from __future__ import annotations

import pygame as pg
from typing import List, Dict, Optional
from collections import deque


class RectPool:
    """
    Object pool for pygame.Rect instances.
    
    Reduces garbage collection overhead by reusing Rect objects
    instead of creating new ones every frame.
    
    Example:
        pool = RectPool(initial_size=50)
        rect = pool.acquire()
        rect.update(100, 100, 32, 32)
        # ... use rect ...
        pool.release(rect)
    """
    
    def __init__(self, initial_size: int = 50, max_size: int = 200) -> None:
        """
        Initialize Rect pool.
        
        Args:
            initial_size: Initial number of pre-allocated Rects
            max_size: Maximum pool size
        """
        self.max_size = max_size
        self._available: deque[pg.Rect] = deque()
        self._in_use: List[pg.Rect] = []
        
        # Pre-allocate initial Rects
        for _ in range(initial_size):
            self._available.append(pg.Rect(0, 0, 0, 0))
    
    def acquire(self) -> pg.Rect:
        """
        Acquire a Rect from the pool.
        
        Returns:
            Rect instance (either recycled or new)
        """
        if self._available:
            rect = self._available.popleft()
        else:
            # Create new if pool is empty
            rect = pg.Rect(0, 0, 0, 0)
        
        self._in_use.append(rect)
        return rect
    
    def acquire_copy(self, other: pg.Rect) -> pg.Rect:
        """
        Acquire a Rect and copy values from another.
        
        Args:
            other: Rect to copy from
            
        Returns:
            New Rect with copied values
        """
        rect = self.acquire()
        rect.update(other.x, other.y, other.width, other.height)
        return rect
    
    def release(self, rect: pg.Rect) -> None:
        """
        Release a Rect back to the pool.
        
        Args:
            rect: Rect to return to pool
        """
        if rect in self._in_use:
            self._in_use.remove(rect)
            
            # Reset rect
            rect.x = 0
            rect.y = 0
            rect.width = 0
            rect.height = 0
            
            # Only keep if under max size
            if len(self._available) < self.max_size:
                self._available.append(rect)
    
    def release_all(self) -> None:
        """Release all in-use Rects back to pool."""
        for rect in list(self._in_use):
            self.release(rect)
    
    @property
    def available_count(self) -> int:
        """Number of Rects available in pool."""
        return len(self._available)
    
    @property
    def in_use_count(self) -> int:
        """Number of Rects currently in use."""
        return len(self._in_use)
    
    @property
    def total_count(self) -> int:
        """Total number of Rects (pooled + in use)."""
        return len(self._available) + len(self._in_use)
    
    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics."""
        return {
            "available": self.available_count,
            "in_use": self.in_use_count,
            "total": self.total_count,
            "max_size": self.max_size,
        }


class TempRectManager:
    """
    Manager for temporary Rect allocations.
    
    Provides short-lived Rect objects that are automatically
    recycled after use.
    
    Example:
        temp_mgr = TempRectManager()
        
        # In game loop:
        temp_mgr.begin_frame()
        rect1 = temp_mgr.get_rect(100, 100, 32, 32)
        rect2 = temp_mgr.get_rect(200, 200, 64, 64)
        # ... use rects ...
        temp_mgr.end_frame()  # All rects recycled
    """
    
    def __init__(self, pool_size: int = 100) -> None:
        """
        Initialize temp Rect manager.
        
        Args:
            pool_size: Initial pool size
        """
        self._pool = RectPool(initial_size=pool_size, max_size=500)
        self._frame_rects: List[pg.Rect] = []
        self._in_frame = False
    
    def begin_frame(self) -> None:
        """Called at start of frame."""
        self._in_frame = True
        self._frame_rects.clear()
    
    def end_frame(self) -> None:
        """Called at end of frame - recycles all temp rects."""
        self._in_frame = False
        for rect in self._frame_rects:
            self._pool.release(rect)
        self._frame_rects.clear()
    
    def get_rect(self, x: int = 0, y: int = 0, w: int = 0, h: int = 0) -> pg.Rect:
        """
        Get a temporary Rect.
        
        Args:
            x, y: Position
            w, h: Size
            
        Returns:
            Rect instance (auto-recycled at end of frame)
        """
        rect = self._pool.acquire()
        rect.update(x, y, w, h)
        
        if self._in_frame:
            self._frame_rects.append(rect)
        
        return rect
    
    def get_rect_copy(self, other: pg.Rect) -> pg.Rect:
        """
        Get a temporary Rect copied from another.
        
        Args:
            other: Rect to copy
            
        Returns:
            Copied Rect instance
        """
        rect = self._pool.acquire_copy(other)
        
        if self._in_frame:
            self._frame_rects.append(rect)
        
        return rect
    
    def get_stats(self) -> Dict[str, int]:
        """Get manager statistics."""
        return self._pool.get_stats()


# Global temp rect manager instance
_temp_rect_manager: Optional[TempRectManager] = None


def get_temp_rect_manager() -> TempRectManager:
    """
    Get global temp Rect manager instance.
    
    Returns:
        TempRectManager instance
    """
    global _temp_rect_manager
    if _temp_rect_manager is None:
        _temp_rect_manager = TempRectManager()
    return _temp_rect_manager


def temp_rect(x: int = 0, y: int = 0, w: int = 0, h: int = 0) -> pg.Rect:
    """
    Convenience function to get a temporary Rect.
    
    Args:
        x, y: Position
        w, h: Size
        
    Returns:
        Rect instance
    """
    return get_temp_rect_manager().get_rect(x, y, w, h)


class ObjectCache:
    """
    Generic object cache for reusable objects.
    
    Similar to object pool but with LRU eviction.
    
    Example:
        cache = ObjectCache(max_size=100)
        obj = cache.get_or_create("key", lambda: ExpensiveObject())
    """
    
    def __init__(self, max_size: int = 100) -> None:
        """
        Initialize object cache.
        
        Args:
            max_size: Maximum cache size
        """
        self.max_size = max_size
        self._cache: Dict[str, object] = {}
        self._access_order: List[str] = []
    
    def get(self, key: str) -> Optional[object]:
        """
        Get cached object.
        
        Args:
            key: Cache key
            
        Returns:
            Cached object or None
        """
        if key in self._cache:
            # Move to end (most recently used)
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None
    
    def put(self, key: str, obj: object) -> None:
        """
        Store object in cache.
        
        Args:
            key: Cache key
            obj: Object to cache
        """
        if key in self._cache:
            self._access_order.remove(key)
        elif len(self._cache) >= self.max_size:
            # Evict least recently used
            lru_key = self._access_order.pop(0)
            del self._cache[lru_key]
        
        self._cache[key] = obj
        self._access_order.append(key)
    
    def get_or_create(self, key: str, factory) -> object:
        """
        Get cached object or create if not exists.
        
        Args:
            key: Cache key
            factory: Function to create object
            
        Returns:
            Cached or newly created object
        """
        obj = self.get(key)
        if obj is None:
            obj = factory()
            self.put(key, obj)
        return obj
    
    def clear(self) -> None:
        """Clear all cached objects."""
        self._cache.clear()
        self._access_order.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
        }
