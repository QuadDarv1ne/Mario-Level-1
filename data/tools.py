"""
Core tools and base classes for the game.
Contains the Control class for game loop management and utility functions.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING
import pygame as pg

if TYPE_CHECKING:
    from pygame.surface import Surface
    from pygame.event import Event

__author__ = "justinarmstrong"

keybinding: Dict[str, int] = {
    "action": pg.K_s,
    "jump": pg.K_a,
    "left": pg.K_LEFT,
    "right": pg.K_RIGHT,
    "down": pg.K_DOWN,
}


class Control:
    """
    Control class for entire project.

    Contains the game loop, and contains the event_loop which passes events
    to States as needed. Logic for flipping states is also found here.

    Attributes:
        screen: Main display surface
        done: Flag to indicate game loop should end
        clock: Pygame clock for FPS control
        caption: Window title
        fps: Target frames per second
        show_fps: Whether to display FPS in window title
        current_time: Current game time in milliseconds
        keys: Current state of keyboard
        state_dict: Dictionary of game states
        state_name: Name of current state
        state: Current state object
    """

    def __init__(self, caption: str) -> None:
        """Initialize the game controller."""
        self.screen: Surface = pg.display.get_surface()
        self.done: bool = False
        self.clock: pg.time.Clock = pg.time.Clock()
        self.caption: str = caption
        self.fps: int = 60
        self.show_fps: bool = False
        self.current_time: float = 0.0
        self.keys: Tuple[bool, ...] = pg.key.get_pressed()
        self.state_dict: Dict[str, _State] = {}
        self.state_name: str = ""
        self.state: Optional[_State] = None

    def setup_states(self, state_dict: Dict[str, _State], start_state: str) -> None:
        """
        Initialize game states.

        Args:
            state_dict: Dictionary mapping state names to State objects
            start_state: Name of the initial state
        """
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    def update(self) -> None:
        """Update current state and check for state transitions."""
        self.current_time = pg.time.get_ticks()
        if self.state is None:
            return
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(self.screen, self.keys, self.current_time)

    def flip_state(self) -> None:
        """Transition to the next state, passing persistent data."""
        if self.state is None:
            return
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, persist)
        self.state.previous = previous

    def event_loop(self) -> None:
        """Process pygame events and pass them to the current state."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                self.toggle_show_fps(event.key)
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            if self.state is not None:
                self.state.get_event(event)

    def toggle_show_fps(self, key: int) -> None:
        """
        Toggle FPS display on/off.

        Args:
            key: The key that was pressed
        """
        if key == pg.K_F5:
            self.show_fps = not self.show_fps
            if not self.show_fps:
                pg.display.set_caption(self.caption)

    def main(self) -> None:
        """Main game loop - processes events, updates state, renders."""
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)
            if self.show_fps:
                fps = self.clock.get_fps()
                with_fps = "{} - {:.2f} FPS".format(self.caption, fps)
                pg.display.set_caption(with_fps)


class _State:
    """
    Base class for all game states.

    Provides common functionality for menu, level, game over screens, etc.
    Subclasses should override: startup, cleanup, update, get_event

    Attributes:
        start_time: Time when state was entered
        current_time: Current time within state
        done: Flag indicating state should transition
        quit: Flag indicating game should exit
        next: Name of next state
        previous: Name of previous state
        persist: Data to pass between states
    """

    def __init__(self) -> None:
        """Initialize state with default values."""
        self.start_time: float = 0.0
        self.current_time: float = 0.0
        self.done: bool = False
        self.quit: bool = False
        self.next: Optional[str] = None
        self.previous: Optional[str] = None
        self.persist: Dict[str, Any] = {}

    def get_event(self, event: Event) -> None:
        """
        Process a single event.

        Args:
            event: Pygame event to process
        """
        pass

    def startup(self, current_time: float, persistant: Dict[str, Any]) -> None:
        """
        Called when state is first entered.

        Args:
            current_time: Current game time in milliseconds
            persistant: Data passed from previous state
        """
        self.persist = persistant
        self.start_time = current_time

    def cleanup(self) -> Dict[str, Any]:
        """
        Called when state is exiting.

        Returns:
            Dictionary of data to pass to next state
        """
        self.done = False
        return self.persist

    def update(self, surface: Surface, keys: Tuple[bool, ...], current_time: float) -> None:
        """
        Update state logic and render.

        Args:
            surface: Display surface to render to
            keys: Current keyboard state
            current_time: Current game time in milliseconds
        """
        pass


def load_all_gfx(
    directory: str, colorkey: Tuple[int, int, int] = (255, 0, 255), accept: Tuple[str, ...] = (".png", ".jpg", ".bmp")
) -> Dict[str, pg.Surface]:
    """Load all graphics from a directory."""
    graphics: Dict[str, pg.Surface] = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name] = img
    return graphics


def load_all_music(directory: str, accept: Tuple[str, ...] = (".wav", ".mp3", ".ogg", ".mdi")) -> Dict[str, str]:
    """Load all music file paths from a directory."""
    songs: Dict[str, str] = {}
    for song in os.listdir(directory):
        name, ext = os.path.splitext(song)
        if ext.lower() in accept:
            songs[name] = os.path.join(directory, song)
    return songs


def load_all_fonts(directory: str, accept: Tuple[str, ...] = (".ttf",)) -> Dict[str, str]:
    """Load all font file paths from a directory."""
    return load_all_music(directory, accept)


def load_all_sfx(
    directory: str, accept: Tuple[str, ...] = (".wav", ".mpe", ".ogg", ".mdi")
) -> Dict[str, pg.mixer.Sound]:
    """Load all sound effects from a directory."""
    effects: Dict[str, pg.mixer.Sound] = {}
    for fx in os.listdir(directory):
        name, ext = os.path.splitext(fx)
        if ext.lower() in accept:
            effects[name] = pg.mixer.Sound(os.path.join(directory, fx))
    return effects
