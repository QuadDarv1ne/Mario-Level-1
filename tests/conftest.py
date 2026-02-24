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
    from types import SimpleNamespace

    class _DummySurface(SimpleNamespace):
        def __init__(self, size=(0, 0)):
            super().__init__()
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

    pg = SimpleNamespace(init=_init, quit=_quit, display=_Display(), time=_Time())

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
