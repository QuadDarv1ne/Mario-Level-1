"""
Pytest configuration and fixtures for Mario Level 1 tests.
"""
from __future__ import annotations

import os
import sys
import pytest
try:
    import pygame as pg
except Exception:  # pragma: no cover - fallback for environments without pygame
    from types import ModuleType, SimpleNamespace
    import sys

    class _DummySurface:
        def __init__(self, size=(0, 0)):
            self._size = tuple(size)

        def get_size(self):
            return self._size

    class _Display:
        def __init__(self):
            self._mode = None

        def set_mode(self, size):
            self._mode = tuple(size)
            return _DummySurface(size)

    class _Time:
        class Clock:
            def tick(self, *_, **__):
                return 0

    def _init():
        return None

    def _quit():
        return None

    pg = ModuleType("pygame")
    pg.init = _init
    pg.quit = _quit
    pg.display = _Display()
    pg.time = _Time()

    # Minimal key constants and event support used in tests
    pg.K_a = ord("a")
    pg.K_s = ord("s")
    pg.K_z = ord("z")
    pg.K_d = ord("d")
    pg.K_w = ord("w")
    pg.K_SPACE = 32
    pg.K_RETURN = 13
    pg.K_BACKSPACE = 8
    pg.K_ESCAPE = 27
    pg.K_LSHIFT = 304
    pg.K_LEFT = 276
    pg.K_RIGHT = 275
    pg.K_UP = 273
    pg.K_DOWN = 274
    pg.K_F3 = 294
    pg.K_F4 = 295
    pg.K_F5 = 296
    pg.K_F9 = 300
    pg.K_F10 = 301
    pg.K_F12 = 303
    pg.K_BACKQUOTE = 96

    class _EventModule:
        KEYDOWN = 1
        KEYUP = 2

        @staticmethod
        def Event(event_type, attrs=None):
            obj = SimpleNamespace()
            obj.type = event_type
            if attrs:
                for k, v in attrs.items():
                    setattr(obj, k, v)
            return obj

    pg.event = _EventModule()
    # Minimal sprite implementation
    class _Sprite:
        def __init__(self):
            self.image = None
            self.rect = None

        def update(self, *_, **__):
            pass

    class _Group:
        def __init__(self):
            self._sprites = []

        def add(self, *sprites):
            for s in sprites:
                if s not in self._sprites:
                    self._sprites.append(s)

        def remove(self, *sprites):
            for s in sprites:
                if s in self._sprites:
                    self._sprites.remove(s)

        def empty(self):
            self._sprites.clear()

        def update(self, *args, **kwargs):
            for s in list(self._sprites):
                if hasattr(s, "update"):
                    s.update(*args, **kwargs)

        def sprites(self):
            return list(self._sprites)

    pg.sprite = SimpleNamespace(Sprite=_Sprite, Group=_Group)

    # Make the dummy pygame available for subsequent imports
    sys.modules["pygame"] = pg

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    """Initialize pygame once per test session."""
    try:
        pg.init()
        pg.display.set_mode((100, 100))
    except Exception:
        # If running with the dummy pygame, the calls are safe no-ops
        pass
    yield
    try:
        pg.quit()
    except Exception:
        pass


@pytest.fixture
def screen():
    """Create a pygame surface for rendering tests."""
    return pg.display.set_mode((800, 600))


@pytest.fixture
def clock():
    """Create a pygame clock for timing tests."""
    return pg.time.Clock()
