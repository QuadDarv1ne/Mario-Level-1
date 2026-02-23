"""
Dialogue and Story System for Super Mario Bros.

Provides:
- Dialogue box with typewriter effect
- Story progression tracking
- Character dialogue definitions
- Branching dialogue trees
- Subtitle support
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Tuple

import pygame as pg

from . import constants as c
from .animation_system import Tween, TweenManager, EasingType


class DialogueAlign(Enum):
    """Text alignment options."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class DialogueSpeed(Enum):
    """Typewriter speed options."""
    SLOW = 50  # ms per character
    NORMAL = 30
    FAST = 15
    INSTANT = 0


@dataclass
class DialogueLine:
    """
    Single line of dialogue.

    Attributes:
        speaker: Character name
        text: Dialogue text
        avatar: Avatar image key (optional)
        align: Text alignment
        speed: Typewriter speed
        next_id: Next dialogue line ID
        choices: Branching choices
        sound_effect: Sound to play
        callback: Function to call when line shown
    """
    speaker: str
    text: str
    avatar: Optional[str] = None
    align: DialogueAlign = DialogueAlign.LEFT
    speed: DialogueSpeed = DialogueSpeed.NORMAL
    next_id: Optional[str] = None
    choices: List[Tuple[str, str]] = field(default_factory=list)  # (text, next_id)
    sound_effect: Optional[str] = None
    callback: Optional[Callable[[], None]] = None


@dataclass
class Character:
    """Character definition for dialogue."""
    name: str
    display_name: str
    color: tuple[int, int, int] = c.WHITE
    avatar: Optional[str] = None
    voice_pitch: float = 1.0


class DialogueBox:
    """
    Dialogue display box with typewriter effect.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        font_size: int = 28
    ) -> None:
        """
        Initialize dialogue box.

        Args:
            x, y: Box position
            width, height: Box dimensions
            font_size: Font size for text
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_size = font_size

        self._init_fonts()

        # State
        self.visible = False
        self.current_line: Optional[DialogueLine] = None
        self.displayed_text = ""
        self.text_index = 0
        self.char_timer = 0
        self.is_typing = False
        self.is_complete = False

        # Animation
        self.tween_manager = TweenManager()
        self.alpha = 0
        self.slide_offset = self.height

        # Configuration
        self.box_color = (20, 20, 40)
        self.border_color = c.GOLD
        self.text_color = c.WHITE
        self.name_color = c.SKY_BLUE

    def _init_fonts(self) -> None:
        """Initialize fonts."""
        try:
            self.font = pg.font.Font(None, self.font_size)
            self.name_font = pg.font.Font(None, self.font_size - 4)
        except pg.error:
            self.font = None
            self.name_font = None

    def show(self, line: DialogueLine) -> None:
        """
        Show dialogue line.

        Args:
            line: Dialogue line to display
        """
        self.current_line = line
        self.displayed_text = ""
        self.text_index = 0
        self.is_typing = True
        self.is_complete = False
        self.visible = True

        # Slide in animation
        self.tween_manager.add_tween(
            "slide",
            self.slide_offset,
            0,
            300,
            EasingType.EASE_OUT_QUAD
        )
        self.slide_offset = self.height

        # Fade in
        self.tween_manager.add_tween(
            "alpha",
            self.alpha,
            255,
            200,
            EasingType.EASE_OUT_SINE
        )
        self.alpha = 255

    def update(self, dt: int) -> None:
        """
        Update dialogue state.

        Args:
            dt: Delta time in milliseconds
        """
        # Update animations
        results = self.tween_manager.update(dt)
        self.slide_offset = int(results.get("slide", self.slide_offset))
        self.alpha = int(results.get("alpha", self.alpha))

        # Update typewriter effect
        if self.is_typing and self.current_line:
            self._update_typewriter(dt)

    def _update_typewriter(self, dt: int) -> None:
        """Update typewriter effect."""
        if not self.current_line:
            return

        self.char_timer += dt
        char_delay = self.current_line.speed.value

        if char_delay == DialogueSpeed.INSTANT.value:
            # Show all text immediately
            self.displayed_text = self.current_line.text
            self.text_index = len(self.current_line.text)
            self.is_typing = False
            self.is_complete = True
            return

        while self.char_timer >= char_delay and self.text_index < len(self.current_line.text):
            self.displayed_text += self.current_line.text[self.text_index]
            self.text_index += 1
            self.char_timer -= char_delay

        if self.text_index >= len(self.current_line.text):
            self.is_typing = False
            self.is_complete = True

    def advance(self) -> bool:
        """
        Advance dialogue.

        Returns:
            True if dialogue should continue, False if complete
        """
        if self.is_typing:
            # Complete text immediately
            self.displayed_text = self.current_line.text if self.current_line else ""
            self.text_index = len(self.displayed_text)
            self.is_typing = False
            self.is_complete = True
            return True

        return False

    def hide(self) -> None:
        """Hide dialogue box."""
        self.visible = False
        self.current_line = None

        # Slide out animation
        self.tween_manager.add_tween(
            "slide",
            self.slide_offset,
            self.height,
            200
        )

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw dialogue box.

        Args:
            surface: Surface to draw to
        """
        if not self.visible:
            return

        # Calculate actual Y position with slide offset
        draw_y = self.y + self.slide_offset

        # Draw background
        box_surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
        box_color = (*self.box_color, int(self.alpha * 0.9))
        pg.draw.rect(box_surface, box_color, (0, 0, self.width, self.height), border_radius=8)

        # Draw border
        border_color = (*self.border_color, self.alpha)
        pg.draw.rect(box_surface, border_color, (0, 0, self.width, self.height), 2, border_radius=8)

        surface.blit(box_surface, (self.x, draw_y))

        # Draw speaker name
        if self.current_line and self.current_line.speaker:
            if self.name_font:
                name_surface = self.name_font.render(
                    self.current_line.speaker,
                    True,
                    self.name_color
                )
                name_surface.set_alpha(self.alpha)
                surface.blit(name_surface, (self.x + 15, draw_y + 10))

        # Draw text
        if self.font and self.displayed_text:
            self._draw_wrapped_text(surface, draw_y)

        # Draw continue indicator
        if self.is_complete:
            self._draw_continue_indicator(surface, draw_y)

    def _draw_wrapped_text(self, surface: pg.Surface, draw_y: int) -> None:
        """Draw wrapped text."""
        if not self.current_line:
            return

        words = self.displayed_text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            test_surface = self.font.render(test_line, True, self.text_color)
            if test_surface.get_width() <= self.width - 30:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        if current_line:
            lines.append(current_line)

        # Draw each line
        text_y = draw_y + 45
        for line in lines[:4]:  # Max 4 lines
            line_surface = self.font.render(line, True, self.text_color)
            line_surface.set_alpha(self.alpha)

            # Alignment
            if self.current_line and self.current_line.align == DialogueAlign.CENTER:
                text_x = self.x + (self.width - line_surface.get_width()) // 2
            elif self.current_line and self.current_line.align == DialogueAlign.RIGHT:
                text_x = self.x + self.width - line_surface.get_width() - 15
            else:
                text_x = self.x + 15

            surface.blit(line_surface, (text_x, text_y))
            text_y += 30

    def _draw_continue_indicator(self, surface: pg.Surface, draw_y: int) -> None:
        """Draw continue indicator (blinking arrow)."""
        blink_speed = 500  # ms
        blink = (time.time() * 1000) % (blink_speed * 2) < blink_speed

        if blink:
            arrow = "▼"
            if self.font:
                arrow_surface = self.font.render(arrow, True, c.GOLD)
                arrow_surface.set_alpha(self.alpha)
                arrow_rect = arrow_surface.get_rect(
                    center=(self.x + self.width - 30, draw_y + self.height - 25)
                )
                surface.blit(arrow_surface, arrow_rect)


class DialogueManager:
    """
    Central manager for dialogue system.
    """

    def __init__(self, dialogue_box: Optional[DialogueBox] = None) -> None:
        """
        Initialize dialogue manager.

        Args:
            dialogue_box: Dialogue box instance (created if None)
        """
        self.dialogue_box = dialogue_box or DialogueBox(50, 400, 700, 150)

        self.dialogues: Dict[str, DialogueLine] = {}
        self.characters: Dict[str, Character] = {}
        self.current_id: Optional[str] = None
        self.is_active = False

        # Callbacks
        self._on_dialogue_start: Optional[Callable[[], None]] = None
        self._on_dialogue_end: Optional[Callable[[], None]] = None
        self._on_line_shown: Optional[Callable[[DialogueLine], None]] = None

    def register_dialogue(self, line_id: str, line: DialogueLine) -> None:
        """
        Register a dialogue line.

        Args:
            line_id: Unique identifier
            line: Dialogue line
        """
        self.dialogues[line_id] = line

    def register_character(self, name: str, character: Character) -> None:
        """
        Register a character.

        Args:
            name: Character name
            character: Character definition
        """
        self.characters[name] = character

    def start(self, dialogue_id: str) -> bool:
        """
        Start dialogue sequence.

        Args:
            dialogue_id: Starting dialogue line ID

        Returns:
            True if dialogue started
        """
        if dialogue_id not in self.dialogues:
            return False

        self.current_id = dialogue_id
        self.is_active = True

        line = self.dialogues[dialogue_id]
        self.dialogue_box.show(line)

        if self._on_dialogue_start:
            self._on_dialogue_start()

        return True

    def update(self, dt: int) -> None:
        """
        Update dialogue system.

        Args:
            dt: Delta time in milliseconds
        """
        self.dialogue_box.update(dt)

    def advance(self) -> bool:
        """
        Advance to next dialogue.

        Returns:
            True if dialogue continues
        """
        if not self.is_active or not self.current_id:
            return False

        # Complete current line
        if not self.dialogue_box.advance():
            return True

        current_line = self.dialogues[self.current_id]

        # Check for choices
        if current_line.choices:
            # Would show choice UI here
            pass

        # Get next line
        next_id = current_line.next_id
        if next_id and next_id in self.dialogues:
            self.current_id = next_id
            next_line = self.dialogues[next_id]
            self.dialogue_box.show(next_line)

            if self._on_line_shown:
                self._on_line_shown(next_line)

            return True

        # End dialogue
        self.end()
        return False

    def end(self) -> None:
        """End dialogue sequence."""
        self.dialogue_box.hide()
        self.is_active = False
        self.current_id = None

        if self._on_dialogue_end:
            self._on_dialogue_end()

    def skip(self) -> None:
        """Skip to end of dialogue."""
        self.end()

    def is_visible(self) -> bool:
        """Check if dialogue is visible."""
        return self.dialogue_box.visible

    def set_on_start(self, callback: Callable[[], None]) -> None:
        """Set dialogue start callback."""
        self._on_dialogue_start = callback

    def set_on_end(self, callback: Callable[[], None]) -> None:
        """Set dialogue end callback."""
        self._on_dialogue_end = callback

    def set_on_line(self, callback: Callable[[DialogueLine], None]) -> None:
        """Set line shown callback."""
        self._on_line_shown = callback


class StoryProgression:
    """
    Track story progression and unlock dialogue.
    """

    def __init__(self) -> None:
        """Initialize story progression."""
        self.completed_events: set[str] = set()
        self.current_chapter: str = "prologue"
        self.flags: Dict[str, bool] = {}
        self.variables: Dict[str, int] = {}

    def mark_event_complete(self, event_id: str) -> None:
        """Mark story event as complete."""
        self.completed_events.add(event_id)

    def is_event_complete(self, event_id: str) -> bool:
        """Check if event is complete."""
        return event_id in self.completed_events

    def set_flag(self, flag_name: str, value: bool) -> None:
        """Set story flag."""
        self.flags[flag_name] = value

    def get_flag(self, flag_name: str, default: bool = False) -> bool:
        """Get story flag value."""
        return self.flags.get(flag_name, default)

    def set_variable(self, var_name: str, value: int) -> None:
        """Set story variable."""
        self.variables[var_name] = value

    def get_variable(self, var_name: str, default: int = 0) -> int:
        """Get story variable value."""
        return self.variables.get(var_name, default)

    def increment_variable(self, var_name: str, amount: int = 1) -> int:
        """Increment story variable."""
        current = self.get_variable(var_name, 0)
        self.variables[var_name] = current + amount
        return self.variables[var_name]

    def set_chapter(self, chapter: str) -> None:
        """Set current chapter."""
        self.current_chapter = chapter

    def get_progress(self) -> dict:
        """Get story progress as dictionary."""
        return {
            "chapter": self.current_chapter,
            "events_completed": len(self.completed_events),
            "flags_set": len(self.flags),
            "variables": self.variables.copy(),
        }


# Default Mario dialogues
MARIO_DIALOGUES = {
    "intro_1": DialogueLine(
        speaker="Марио",
        text="Давайте начнём! Нужно добраться до флага!",
        speed=DialogueSpeed.NORMAL,
        next_id="intro_2"
    ),
    "intro_2": DialogueLine(
        speaker="Марио",
        text="Собирайте монеты и побеждайте врагов!",
        speed=DialogueSpeed.NORMAL,
        next_id=None
    ),
    "first_mushroom": DialogueLine(
        speaker="Марио",
        text="Супер-гриб! Я стану большим!",
        speed=DialogueSpeed.FAST,
        next_id=None
    ),
    "first_fireflower": DialogueLine(
        speaker="Марио",
        text="Огненный цветок! Теперь я могу бросаться огнём!",
        speed=DialogueSpeed.FAST,
        next_id=None
    ),
    "low_time": DialogueLine(
        speaker="Марио",
        text="Время заканчивается! Нужно спешить!",
        speed=DialogueSpeed.NORMAL,
        next_id=None
    ),
    "near_flag": DialogueLine(
        speaker="Марио",
        text="Флаг близко! Почти у цели!",
        speed=DialogueSpeed.NORMAL,
        next_id=None
    ),
}

LUIGI_DIALOGUES = {
    "intro": DialogueLine(
        speaker="Луиджи",
        text="Марио, будь осторожен! Там много врагов!",
        speed=DialogueSpeed.NORMAL,
        next_id=None
    ),
}

TOAD_DIALOGUES = {
    "greeting": DialogueLine(
        speaker="Тод",
        text="Привет! Я видел принцессу в другом замке!",
        speed=DialogueSpeed.NORMAL,
        next_id=None
    ),
    "hint": DialogueLine(
        speaker="Тод",
        text="Попробуй разбить некоторые блоки. В них могут быть секреты!",
        speed=DialogueSpeed.NORMAL,
        next_id=None
    ),
}

BOWSER_DIALOGUES = {
    "taunt_1": DialogueLine(
        speaker="Боузер",
        text="Ха-ха-ха! Тебе не победить меня!",
        speed=DialogueSpeed.NORMAL,
        next_id=None
    ),
    "defeated": DialogueLine(
        speaker="Боузер",
        text="Нет! Это невозможно!",
        speed=DialogueSpeed.FAST,
        next_id=None
    ),
}


def create_default_dialogues() -> DialogueManager:
    """
    Create dialogue manager with default Mario dialogues.

    Returns:
        Configured DialogueManager
    """
    manager = DialogueManager()

    # Register characters
    manager.register_character("mario", Character(
        name="mario",
        display_name="Марио",
        color=c.RED
    ))
    manager.register_character("luigi", Character(
        name="luigi",
        display_name="Луиджи",
        color=c.GREEN
    ))
    manager.register_character("toad", Character(
        name="toad",
        display_name="Тод",
        color=c.SKY_BLUE
    ))
    manager.register_character("bowser", Character(
        name="bowser",
        display_name="Боузер",
        color=c.ORANGE
    ))

    # Register dialogues
    for line_id, line in MARIO_DIALOGUES.items():
        manager.register_dialogue(line_id, line)

    for line_id, line in LUIGI_DIALOGUES.items():
        manager.register_dialogue(line_id, line)

    for line_id, line in TOAD_DIALOGUES.items():
        manager.register_dialogue(line_id, line)

    for line_id, line in BOWSER_DIALOGUES.items():
        manager.register_dialogue(line_id, line)

    return manager
