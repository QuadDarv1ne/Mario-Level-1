# Changelog

All notable changes to this project will be documented in this file.

## [2.5.0] - 2026-02-23

### Added

#### Dialogue System (`data/dialogue_system.py`)
- **Dialogue box** with typewriter text effect
- **Character definitions** with colors and avatars
- **Branching dialogue trees** with choices
- **Story progression tracking** with flags and variables
- **17+ built-in dialogues** for Mario characters
- **Configurable text speed** (slow, normal, fast, instant)
- **Slide and fade animations** for dialogue display

#### Screenshot System (`data/screenshot.py`)
- **Screenshot capture** with auto-numbering
- **Event-based auto-screenshots** (level complete, powerup, etc.)
- **Screenshot gallery** with HTML export
- **Metadata tracking** (timestamp, resolution, game state)
- **Tag-based organization**
- **Multiple formats** (PNG, JPG, BMP)
- **Cooldown protection** against spam

#### Debug Utilities (`data/debug.py`)
- **Debug overlay** with FPS, memory, sprite count
- **Collision visualizer** for hitboxes
- **Entity inspector** for runtime debugging
- **Debug console** with commands
- **Performance profiler** for timing code
- **Hotkey support**: F3 (overlay), F4 (collisions), F5 (inspector), ` (console)

#### Statistics System (`data/statistics.py`)
- **Session statistics** tracking
- **Lifetime statistics** across all sessions
- **Enemy-specific stats** (Goombas, Koopas, etc.)
- **Power-up statistics** tracking
- **Record tracking** (high score, most coins, etc.)
- **Stats persistence** with JSON saves
- **Stats display UI**

#### New Tests
- `tests/test_dialogue_system.py` - 25+ tests
- `tests/test_screenshot.py` - 20+ tests
- `tests/test_debug.py` - 25+ tests
- `tests/test_statistics.py` - 25+ tests

### Changed

#### Updated Files
- `data/__init__.py` - Added new module exports, version 2.5.0
- `CHANGELOG.md` - This entry

### Technical Details

#### New Modules
- `data/dialogue_system.py` - Dialogue and story (~500 lines)
- `data/screenshot.py` - Screenshot management (~350 lines)
- `data/debug.py` - Debug utilities (~550 lines)
- `data/statistics.py` - Statistics tracking (~400 lines)

#### Test Coverage
- Total tests: 320+
- New test files: 4
- Coverage areas: dialogue, screenshot, debug, statistics

---

## [2.4.0] - 2026-02-23

### Added

#### Weather System (`data/weather_system.py`)
- **Dynamic weather effects**: Rain, snow, clouds, storm, wind
- **Day/night cycle** with smooth sky color transitions
- **8 time periods**: Dawn, Morning, Noon, Afternoon, Dusk, Evening, Night, Midnight
- **Configurable cycle duration** and time scale
- **Seasonal themes**: Spring, Summer, Autumn, Winter
- **Lightning effects** for stormy weather
- **Weather intensity control** (0-1 scale)

#### Advanced Audio Manager (`data/audio_manager.py`)
- **Multi-channel audio** with 16 simultaneous sound channels
- **Sound effect pooling** for efficient audio playback
- **Music playlist system** with shuffle and repeat
- **5 audio categories**: Music, SFX, Voice, Ambient, UI
- **Category-based volume control**
- **Audio fade effects** (fade in/out)
- **Priority-based sound** channel allocation
- **Pre-configured game sounds** for Mario actions
- **Audio statistics** tracking

#### Hint System (`data/hint_system.py`)
- **Context-sensitive hints** based on player actions
- **17+ built-in hints** covering all game mechanics
- **Hint categories**: Movement, Combat, Power-ups, Secrets, Enemies, Collection
- **Priority system**: Low, Normal, High, Critical
- **Prerequisite chain** for progressive hint unlocking
- **Configurable trigger counts** and cooldowns
- **Hint display UI** with fade animations
- **Event trigger system** for game integration
- **Condition-based hints** (player level, defeats, coins, deaths)
- **Tutorial mode** for new players

#### New Tests
- `tests/test_weather_system.py` - 25+ tests for weather/day-night
- `tests/test_audio_manager.py` - 30+ tests for audio system
- `tests/test_hint_system.py` - 30+ tests for hint system

### Changed

#### Updated Files
- `data/__init__.py` - Added new module exports, version 2.4.0
- `CHANGELOG.md` - This entry

### Technical Details

#### New Modules
- `data/weather_system.py` - Weather and day/night cycle (~550 lines)
- `data/audio_manager.py` - Advanced audio management (~650 lines)
- `data/hint_system.py` - Hint and tutorial system (~600 lines)

#### Test Coverage
- Total tests: 230+
- New test files: 3
- Coverage areas: weather, audio, hints

---

## [2.3.0] - 2026-02-23

### Added

#### Achievements System (`data/achievements.py`)
- **20+ achievements** across multiple tiers (Bronze, Silver, Gold, Platinum, Legendary)
- Persistent achievement tracking with JSON saves
- Unlock notifications with visual feedback
- Statistics tracking (coins, enemies, power-ups, etc.)
- Achievement UI with completion percentage
- Tier-based completion tracking

#### Combo System (`data/combo_system.py`)
- **Score multipliers** for consecutive actions
- Combo tiers (Bronze, Silver, Gold, Platinum, Legendary)
- Configurable combo windows and decay
- Multiple combo types (stomp, coin, block, fireball)
- Combo UI with animated display
- Integration with score system

#### Advanced Animation System (`data/animation_system.py`)
- **Interpolated sprites** for smooth rendering
- **12 easing functions** (linear, quad, cubic, sine, bounce)
- Animation state machines with frame callbacks
- Tween manager for value animations
- Sprite batching with depth sorting
- Support for flip, rotation, scale, alpha

#### Enhanced UI System (`data/ui.py`)
- **Animated main menu** with Russian localization
- **Pause menu** with resume/restart options
- **Interactive buttons** with hover effects and animations
- **HUD improvements** with combo display
- UI manager for centralized control
- Menu transitions with fade effects

#### Difficulty Settings (`data/game_settings.py`)
- **4 difficulty levels**: Easy, Normal, Hard, Extreme
- Configurable enemy behavior per difficulty
- Player speed, jump, health adjustments
- Score multipliers and time limits
- Persistent settings with JSON saves
- Video, audio, and control settings

#### New Tests
- `tests/test_achievements.py` - 25+ tests for achievements
- `tests/test_combo_system.py` - 20+ tests for combo system
- `tests/test_game_settings.py` - 25+ tests for settings
- `tests/test_animation_system.py` - 30+ tests for animations
- `tests/test_ui.py` - 25+ tests for UI components

### Changed

#### Updated Files
- `data/__init__.py` - Added new module exports, version 2.3.0
- `README.md` - Updated with v2.3 features
- `CHANGELOG.md` - This entry

### Technical Details

#### New Modules
- `data/achievements.py` - Achievement tracking and notifications
- `data/combo_system.py` - Combo and score multipliers
- `data/game_settings.py` - Settings and difficulty management
- `data/animation_system.py` - Interpolated animations
- `data/ui.py` - UI components and menus

#### Test Coverage
- Total tests: 150+
- Coverage areas: achievements, combo, settings, animations, UI

---

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

## Future Plans (v2.5+)

### Completed in v2.4
- [x] Weather system with day/night cycle
- [x] Advanced audio manager
- [x] Hint/tutorial system

### Completed in v2.3
- [x] Achievements system
- [x] Combo system with score multipliers
- [x] Advanced animation system
- [x] Enhanced UI with animated menus
- [x] Difficulty settings

### Planned
- [ ] Additional levels (1-2, 1-3, 1-4)
- [ ] Boss battles (Bowser)
- [ ] Multiplayer support (local co-op)
- [ ] Level editor GUI
- [ ] Mobile/touch controls
- [ ] Online leaderboards
- [ ] Sound theme selector
- [ ] Replay system
- [ ] Steam achievements integration
- [ ] Controller/gamepad support
- [ ] Level randomizer mode
- [ ] Time attack mode
