"""
Pytest configuration and fixtures for Mario Level 1 tests.
"""
from __future__ import annotations

import os
import sys
import pytest
import pygame as pg

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    """Initialize pygame once per test session."""
    pg.init()
    pg.display.set_mode((100, 100))
    yield
    pg.quit()


@pytest.fixture
def screen():
    """Create a pygame surface for rendering tests."""
    return pg.display.set_mode((800, 600))


@pytest.fixture
def clock():
    """Create a pygame clock for timing tests."""
    return pg.time.Clock()
