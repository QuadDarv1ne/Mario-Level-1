# Super Mario Bros Level 1 - Enhanced Edition

![screenshot](screenshot.png)

An enhanced recreation of the first level of Super Mario Bros for the NES, built with Python and Pygame.

## 🎮 Controls

| Key | Action |
|-----|--------|
| Arrow Keys | Move left/right, crouch |
| `A` | Jump |
| `S` | Action (fireball, run) |
| `F5` | Toggle FPS display |

## ✨ New Features (v2.0)

### Core Improvements
- **Modern Python**: Now requires Python 3.10+ with full type hints
- **JSON Level Loader**: Load and create levels from JSON files
- **Save System**: Persistent game progress with JSON saves
- **Improved Audio**: Volume control, better mixing, error handling
- **Performance Optimization**: Object pooling, sprite batching
- **Visual Effects**: Particle system, parallax scrolling, screen shake

### Developer Tools
- **Testing**: Full pytest test suite
- **CI/CD**: GitHub Actions for automated testing and builds
- **Code Quality**: pre-commit hooks, mypy, flake8, black
- **Documentation**: Comprehensive docstrings throughout

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Optional: Development Setup

```bash
# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v

# Type checking
mypy data/

# Code formatting
black data/ tests/
```

## 🚀 Running the Game

```bash
python mario_level_1.py
```

Or on Windows:
```bash
python mario_level_1.py
```

## 📁 Project Structure

```
Mario-Level-1/
├── mario_level_1.py      # Main entry point
├── requirements.txt      # Python dependencies
├── pyproject.toml       # Project configuration
├── .pre-commit-config.yaml
├── data/
│   ├── __init__.py
│   ├── main.py          # Game initialization
│   ├── constants.py     # Game constants (typed)
│   ├── tools.py         # Base classes (Control, State)
│   ├── setup.py         # Resource loading
│   ├── level_loader.py  # JSON level loading
│   ├── save_system.py   # Game save/load
│   ├── optimization.py  # Object pooling, batching
│   ├── game_sound.py    # Enhanced audio system
│   ├── visual_effects.py # Particles, parallax
│   ├── components/      # Game objects
│   │   ├── mario.py
│   │   ├── enemies.py
│   │   ├── bricks.py
│   │   └── ...
│   ├── states/          # Game states
│   │   ├── main_menu.py
│   │   ├── level1.py
│   │   └── ...
│   └── levels/          # JSON level files
│       └── level_1_1.json
├── tests/
│   ├── test_level_loader.py
│   ├── test_constants.py
│   ├── test_tools.py
│   └── test_save_system.py
├── resources/
│   ├── graphics/
│   ├── sound/
│   └── fonts/
└── saves/               # Auto-created save directory
```

## 🛠️ Configuration

### Video Settings
Edit `data/constants.py`:
```python
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
```

### Audio Settings
The sound system supports volume control:
```python
from data.game_sound import SoundSettings

settings = SoundSettings()
settings.music_volume = 0.5  # 50%
settings.sfx_volume = 0.7    # 70%
```

### Key Bindings
Edit `data/tools.py`:
```python
keybinding = {
    'action': pg.K_s,
    'jump': pg.K_a,
    'left': pg.K_LEFT,
    'right': pg.K_RIGHT,
    'down': pg.K_DOWN
}
```

## 📝 Creating Custom Levels

Levels can be created in JSON format:

```json
{
  "name": "1-1",
  "width": 8550,
  "ground_height": 538,
  "bricks": [
    {"x": 858, "y": 365, "contents": null}
  ],
  "coin_boxes": [
    {"x": 685, "y": 365, "contents": "coin"}
  ],
  "enemies": [
    {"type": "goomba", "x": 0, "y": 538, "direction": "left"}
  ]
}
```

Save to `data/levels/` and load with:
```python
from data.level_loader import load_level_from_json
level = load_level_from_json("data/levels/my_level.json")
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=data --cov-report=html

# Run specific test file
pytest tests/test_level_loader.py -v
```

## 📊 Performance

The enhanced version includes several optimizations:

| Feature | Improvement |
|---------|-------------|
| Object Pooling | Reduced GC overhead |
| Sprite Batching | Fewer draw calls |
| Type Hints | Better IDE support |
| Lazy Loading | Faster startup |

## 🐛 Known Issues

- Some animations may stutter on low-end hardware
- Audio latency on some Windows configurations

## 📄 License

This project is intended for **non-commercial educational purposes only**.

Super Mario Bros is a trademark of Nintendo.

## 🙏 Credits

**Original Author:** justinarmstrong  
**Enhanced Version:** Community contributions  
**Based on:** Super Mario Bros (Nintendo, 1985)

## 🔗 Links

- [Original YouTube Demo](http://www.youtube.com/watch?v=HBbzYKMfx5Y)
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

## Version History

### v2.0.0 (2026) - Enhanced Edition
- ✅ Python 3.10+ with type hints
- ✅ JSON level loader
- ✅ Save/load system
- ✅ Test suite (pytest)
- ✅ CI/CD pipeline
- ✅ Enhanced audio system
- ✅ Visual effects (particles, parallax)
- ✅ Performance optimizations

### v1.0.0 (2023)
- Original release

---

*Last updated: February 2026*
