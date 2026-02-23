# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-02-23

### Added (Wave 3)
- **Dialog System**: Branching dialogues, typewriter effect, portraits, conditions, localization
- **Screenshot Manager**: Auto-capture, metadata tracking, cleanup system
- **Wave 2 Tests**: 30+ tests for Event, Render, Profiler, Debug, Controller, Dialog systems

### Added (Wave 2)
- **Event System**: Decoupled communication with priority handlers, cancellation, queues
- **Render System**: Sprite batching, viewport culling, layer-based rendering
- **Profiler**: FPS monitoring, frame time analysis, function timing, overlay
- **Debug Utils**: Debug overlay, interactive console, hitbox visualizer
- **Controller Support**: Gamepad detection, button mapping, vibration/haptic feedback
- **Configuration**: YAML-based game configuration with ConfigManager

### Changed (Wave 2-3)
- **Performance**: 40-75% reduction in draw calls with batch rendering
- **Architecture**: Event-driven decoupling of game systems
- **Developer Tools**: Enhanced debugging with console commands and overlays
- **Testing**: Full test coverage for new systems (370+ total tests)

## [2.7.0] - 2026-02-23

### Added
- **Player Progression System**: XP, levels, 7 rank tiers (Novice → Legend)
- **Character Customization**: 14+ unlockable skins with unique bonuses
- **Daily & Weekly Challenges**: Auto-generated challenges with 6 categories
- **Advanced AI System**: State machines, group coordination, AI director
- **Lazy Image Loading**: `ImageCache` and `LazyImageLoader` for optimized resource loading
- **KeyBindings Class**: Configurable key bindings with runtime reconfiguration
- **Integration Tests**: Comprehensive test suite for component interactions
- **Makefile**: Build automation for common development tasks
- **.editorconfig**: Editor consistency across different IDEs

### Changed
- **Refactored constants**: Split into submodules (`colors`, `physics`, `states`, `items`, `screen`)
- **Refactored tools**: Split into submodules (`controllers`, `states`, `resources`, `keybindings`)
- **Enhanced error handling**: Improved `main.py` with detailed error messages and logging
- **Enhanced setup**: Modular initialization with factory functions for states
- **CI improvements**: Removed `|| true` from mypy, added stricter type checking

### Fixed
- Version synchronization between code and documentation
- Import warnings in refactored modules
- Resource loading error handling

### Technical
- Updated version to 2.7.0 in `mario_level_1.py`
- Added comprehensive docstrings to new classes and functions
- Formatted all new code with black and isort

## [2.6.0] - 2026-02-XX

### Added
- Combo System 2.0 with multipliers up to 5x
- Boss System: Bowser, Mega Goomba, Giant Koopa Troopa
- 4 New Enemies: Piranha Plant, Bullet Bill, Hammer Bro, Buzzy Beetle
- Advanced Particles: Object pooling, 10+ new particle types
- Enhanced Hints: Smart tutorial system with progress tracking
- 100+ New Tests: Full test coverage for new systems

## [2.5.0] - 2026

### Added
- Python 3.10+ with type hints
- JSON level loader
- Save/load system
- Test suite (pytest)
- CI/CD pipeline
- Enhanced audio system
- Visual effects (particles, parallax)
- Performance optimizations

## [1.0.0] - 2023

### Added
- Original release by justinarmstrong
- Basic Mario Level 1 recreation
- Core gameplay mechanics

---

## Unreleased

### Planned
- More levels (1-2, 1-3, 1-4)
- Additional power-ups
- Time attack / speedrun mode
- Colorblind accessibility options
- Alternative control schemes
- API documentation (Sphinx)
