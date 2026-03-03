"""Tests for memory optimization utilities."""

from __future__ import annotations

import pytest
import pygame as pg

from data.memory_pool import (
    RectPool,
    TempRectManager,
    ObjectCache,
    get_temp_rect_manager,
    temp_rect,
)


class TestRectPool:
    """Tests for RectPool class."""

    def test_creation(self) -> None:
        """Test RectPool creation."""
        pool = RectPool(initial_size=10, max_size=50)
        
        assert pool.available_count == 10
        assert pool.in_use_count == 0
        assert pool.total_count == 10
        assert pool.max_size == 50

    def test_acquire(self) -> None:
        """Test acquiring a Rect."""
        pool = RectPool(initial_size=5)
        
        rect = pool.acquire()
        
        assert isinstance(rect, pg.Rect)
        assert pool.in_use_count == 1
        assert pool.available_count == 4

    def test_acquire_empty_pool(self) -> None:
        """Test acquiring when pool is empty."""
        pool = RectPool(initial_size=1, max_size=1)
        
        rect1 = pool.acquire()
        rect2 = pool.acquire()  # Should create new
        
        assert isinstance(rect1, pg.Rect)
        assert isinstance(rect2, pg.Rect)
        assert rect1 is not rect2
        assert pool.in_use_count == 2

    def test_release(self) -> None:
        """Test releasing a Rect."""
        pool = RectPool(initial_size=5)
        
        rect = pool.acquire()
        pool.release(rect)
        
        assert pool.in_use_count == 0
        assert pool.available_count == 5

    def test_release_not_in_use(self) -> None:
        """Test releasing Rect not in use."""
        pool = RectPool(initial_size=5)
        
        rect = pg.Rect(0, 0, 10, 10)  # Not from pool
        pool.release(rect)  # Should not raise
        
        assert pool.in_use_count == 0

    def test_release_respects_max_size(self) -> None:
        """Test that release respects max size."""
        pool = RectPool(initial_size=2, max_size=2)
        
        rect1 = pool.acquire()
        rect2 = pool.acquire()
        
        # Acquire one more (creates new)
        rect3 = pool.acquire()
        
        # Release all
        pool.release(rect1)
        pool.release(rect2)
        pool.release(rect3)  # Should not be kept (over max)
        
        assert pool.available_count == 2  # Max size

    def test_release_all(self) -> None:
        """Test releasing all Rects."""
        pool = RectPool(initial_size=5)
        
        rects = [pool.acquire() for _ in range(5)]
        pool.release_all()
        
        assert pool.in_use_count == 0
        assert pool.available_count == 5

    def test_acquire_copy(self) -> None:
        """Test acquiring a copy of another Rect."""
        pool = RectPool(initial_size=5)
        
        original = pg.Rect(100, 200, 32, 64)
        copy = pool.acquire_copy(original)
        
        assert copy.x == 100
        assert copy.y == 200
        assert copy.width == 32
        assert copy.height == 64
        assert copy is not original

    def test_get_stats(self) -> None:
        """Test getting statistics."""
        pool = RectPool(initial_size=10, max_size=50)
        
        rect = pool.acquire()
        stats = pool.get_stats()
        
        assert stats["available"] == 9
        assert stats["in_use"] == 1
        assert stats["total"] == 10
        assert stats["max_size"] == 50


class TestTempRectManager:
    """Tests for TempRectManager class."""

    def test_creation(self) -> None:
        """Test TempRectManager creation."""
        manager = TempRectManager(pool_size=20)
        
        assert manager._pool.available_count == 20
        assert manager._in_frame is False

    def test_begin_frame(self) -> None:
        """Test begin_frame."""
        manager = TempRectManager()
        
        manager.begin_frame()
        
        assert manager._in_frame is True
        assert len(manager._frame_rects) == 0

    def test_end_frame(self) -> None:
        """Test end_frame recycles rects."""
        manager = TempRectManager(pool_size=10)
        
        manager.begin_frame()
        rect = manager.get_rect(10, 10, 20, 20)
        manager.end_frame()
        
        assert manager._in_frame is False
        assert len(manager._frame_rects) == 0
        assert manager._pool.in_use_count == 0

    def test_get_rect(self) -> None:
        """Test getting a temp Rect."""
        manager = TempRectManager()
        
        manager.begin_frame()
        rect = manager.get_rect(100, 200, 32, 64)
        
        assert rect.x == 100
        assert rect.y == 200
        assert rect.width == 32
        assert rect.height == 64
        assert rect in manager._frame_rects
        
        manager.end_frame()

    def test_get_rect_copy(self) -> None:
        """Test getting a copy of another Rect."""
        manager = TempRectManager()
        
        original = pg.Rect(50, 60, 10, 20)
        
        manager.begin_frame()
        copy = manager.get_rect_copy(original)
        
        assert copy.x == 50
        assert copy.y == 60
        assert copy.width == 10
        assert copy.height == 20
        
        manager.end_frame()

    def test_get_stats(self) -> None:
        """Test getting statistics."""
        manager = TempRectManager(pool_size=20)
        
        manager.begin_frame()
        manager.get_rect(0, 0, 10, 10)
        
        stats = manager.get_stats()
        
        assert stats["available"] == 19
        assert stats["in_use"] == 1


class TestGetTempRectManager:
    """Tests for global temp rect manager."""

    def test_singleton(self) -> None:
        """Test that global instance is singleton."""
        manager1 = get_temp_rect_manager()
        manager2 = get_temp_rect_manager()
        
        assert manager1 is manager2


class TestTempRectFunction:
    """Tests for temp_rect convenience function."""

    def test_temp_rect(self) -> None:
        """Test temp_rect function."""
        rect = temp_rect(100, 200, 32, 64)
        
        assert rect.x == 100
        assert rect.y == 200
        assert rect.width == 32
        assert rect.height == 64


class TestObjectCache:
    """Tests for ObjectCache class."""

    def test_creation(self) -> None:
        """Test ObjectCache creation."""
        cache = ObjectCache(max_size=50)
        
        assert cache.max_size == 50
        assert len(cache._cache) == 0

    def test_put_get(self) -> None:
        """Test putting and getting objects."""
        cache = ObjectCache()
        
        obj = object()
        cache.put("key", obj)
        
        assert cache.get("key") is obj

    def test_get_missing(self) -> None:
        """Test getting missing key."""
        cache = ObjectCache()
        
        assert cache.get("missing") is None

    def test_get_or_create_existing(self) -> None:
        """Test get_or_create with existing key."""
        cache = ObjectCache()
        
        obj = object()
        cache.put("key", obj)
        
        result = cache.get_or_create("key", lambda: object())
        
        assert result is obj

    def test_get_or_create_new(self) -> None:
        """Test get_or_create with new key."""
        cache = ObjectCache()
        
        created = []
        
        def factory():
            obj = object()
            created.append(obj)
            return obj
        
        result = cache.get_or_create("new_key", factory)
        
        assert len(created) == 1
        assert result is created[0]
        assert cache.get("new_key") is result

    def test_lru_eviction(self) -> None:
        """Test LRU eviction when cache is full."""
        cache = ObjectCache(max_size=2)
        
        obj1 = object()
        obj2 = object()
        obj3 = object()
        
        cache.put("key1", obj1)
        cache.put("key2", obj2)
        
        # Access key1 to make it recently used
        cache.get("key1")
        
        # Add key3 - should evict key2 (least recently used)
        cache.put("key3", obj3)
        
        assert cache.get("key1") is obj1
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") is obj3

    def test_clear(self) -> None:
        """Test clearing cache."""
        cache = ObjectCache()
        
        cache.put("key1", object())
        cache.put("key2", object())
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_get_stats(self) -> None:
        """Test getting statistics."""
        cache = ObjectCache(max_size=100)
        
        cache.put("key1", object())
        cache.put("key2", object())
        
        stats = cache.get_stats()
        
        assert stats["size"] == 2
        assert stats["max_size"] == 100
