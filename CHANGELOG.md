# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-02-22

### Added

#### Core Features
- **JSON Level Loader** (`data/level_loader.py`)
  - Load levels from JSON files
  - Support for Tiled map editor format
  - Programmatic level creation
  - Save/load level data

- **Save System** (`data/save_system.py`)
  - Persistent game progress
  - JSON-based save files
  - Automatic save directory management
  - Save file metadata

- **Visual Effects** (`data/visual_effects.py`)
  - Particle system for brick breaks, coins, explosions
  - Parallax scrolling background
  - Screen shake effects
  - Fade transitions

- **Optimization Module** (`data/optimization.py`)
  - Generic object pooling
  - Fireball-specific pool
  - Sprite batching for efficient rendering
  - Performance monitoring utilities

#### Developer Tools
- **Test Suite** (`tests/`)
  - Level loader tests
  - Constants tests
  - Tools tests
  - Save system tests
  - Pytest configuration

- **CI/CD Pipeline** (`.github/workflows/ci.yml`)
  - Automated testing on Windows, Linux, macOS
  - Python 3.10, 3.11, 3.12 support
  - Code coverage reporting
  - Executable builds

- **Code Quality Tools**
  - `.pre-commit-config.yaml` for git hooks
  - `pyproject.toml` with black, isort, mypy config
  - `.flake8` configuration
  - Type hints throughout codebase

#### Documentation
- Comprehensive README with installation, usage, and configuration
- API documentation in docstrings
- This CHANGELOG

### Changed

#### Updated Files
- `requirements.txt` - Updated to pygame>=2.5.0, added dev dependencies
- `mario_level_1.py` - Python 3.10+ shebang, enhanced docstring
- `data/constants.py` - Type hints, organized sections, new timing/score constants
- `data/tools.py` - Full type hints, comprehensive docstrings
- `data/game_sound.py` - Type hints, volume control, error handling, new methods
- `data/__init__.py` - Package documentation, exports
- `.gitignore` - Expanded for Python/Pygame projects
- `README.md` - Complete rewrite with all new features

#### Bug Fixes
- Fixed `==` vs `=` typo in `data/states/level1.py:455`
- Replaced magic numbers with named constants
- Fixed audio looping issues

### Improved

#### Audio System
- Volume control for music and SFX
- Better error handling for missing audio files
- Multiple audio channels (16)
- Fade in/out support
- Pause/unpause functionality

#### Code Quality
- Full type hint coverage in core modules
- Comprehensive docstrings
- Consistent code formatting (black)
- Import sorting (isort)

### Technical Details

#### New Dependencies
- pygame>=2.5.0 (was 1.9.1)
- pytest>=7.4.0
- mypy>=1.5.0
- black>=23.0.0
- flake8>=6.1.0
- pre-commit>=3.4.0
- pytmx>=3.29.0 (optional)

#### Breaking Changes
- Requires Python 3.10+ (was 2.7/3.5)
- Requires pygame 2.5+ (was 1.9.1)

---

## [1.0.0] - 2023-01-24

### Original Release
- Basic Super Mario Bros Level 1 recreation
- Mario movement, jumping, power-ups
- Enemies (Goombas, Koopas)
- Brick breaking, coin boxes
- Flag pole completion
- Sound effects and music
- Score system

---

## Migration Guide (v1 → v2)

### For Players
1. Update Python to 3.10+
2. Run `pip install -r requirements.txt`
3. Game runs the same way: `python mario_level_1.py`

### For Developers
1. Install pre-commit hooks: `pre-commit install`
2. Run tests: `pytest tests/ -v`
3. Type check: `mypy data/`

### Code Changes
If you've modified the codebase:

```python
# Old (v1)
import pygame as pg
from data import constants as c

# New (v2) - same imports work, but now with types
from typing import Any
import pygame as pg
from data import constants as c

# All modules now have type hints
def update(self, surface: pg.Surface, keys: dict, time: float) -> None:
    pass
```

---

## Future Plans (v2.1+)

- [ ] Additional levels (1-2, 1-3, 1-4)
- [ ] Boss battles (Bowser)
- [ ] Multiplayer support
- [ ] Level editor GUI
- [ ] Mobile/touch controls
- [ ] Achievements system
- [ ] Online leaderboards
