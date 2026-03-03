"""
Input Buffering System for Super Mario Bros.

Provides:
- Input buffer for responsive controls
- Combo input detection
- Input history tracking
- Configurable buffer windows
- Queue-based input processing
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Callable, Deque

import pygame as pg


class InputType(Enum):
    """Types of input actions."""

    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    JUMP = "jump"
    JUMP_HELD = "jump_held"
    ACTION = "action"
    ACTION_HELD = "action_held"
    PAUSE = "pause"
    QUIT = "quit"


@dataclass
class InputEvent:
    """
    Buffered input event.

    Attributes:
        input_type: Type of input
        timestamp: When input occurred (ms)
        duration: How long input was held (ms)
        consumed: Whether input was processed
    """

    input_type: InputType
    timestamp: float
    duration: int = 0
    consumed: bool = False
    position: tuple[int, int] = (0, 0)  # For mouse/touch


@dataclass
class InputConfig:
    """Configuration for input buffering."""

    # Buffer window in milliseconds
    buffer_window: int = 150
    # Max buffered inputs
    max_buffer_size: int = 10
    # Hold duration to trigger held action
    hold_threshold: int = 300
    # Input queue size for combos
    combo_queue_size: int = 5
    # Deadzone for analog input
    deadzone: float = 0.1


class InputBuffer:
    """
    Buffer for storing and processing input events.

    Usage:
        buffer = InputBuffer()
        buffer.add(InputType.JUMP)
        input_event = buffer.get_oldest()
    """

    def __init__(self, config: Optional[InputConfig] = None) -> None:
        """
        Initialize input buffer.

        Args:
            config: Input configuration
        """
        self.config = config or InputConfig()
        self.buffer: Deque[InputEvent] = deque(maxlen=self.config.max_buffer_size)
        self.combo_queue: Deque[InputEvent] = deque(maxlen=self.config.combo_queue_size)

        self._current_time = 0.0
        self._hold_timers: Dict[InputType, float] = {}

    def add(self, input_type: InputType, position: tuple[int, int] = (0, 0)) -> InputEvent:
        """
        Add input to buffer.

        Args:
            input_type: Type of input
            position: Input position (for mouse/touch)

        Returns:
            Created input event
        """
        self._current_time = time.time() * 1000

        event = InputEvent(input_type=input_type, timestamp=self._current_time, position=position)

        self.buffer.append(event)
        self.combo_queue.append(event)

        # Start hold timer
        self._hold_timers[input_type] = self._current_time

        return event

    def release(self, input_type: InputType) -> Optional[InputEvent]:
        """
        Mark input as released.

        Args:
            input_type: Type of input

        Returns:
            Input event with duration, or None
        """
        self._current_time = time.time() * 1000

        if input_type in self._hold_timers:
            start_time = self._hold_timers[input_type]
            duration = int(self._current_time - start_time)

            # Find and update the event
            for event in reversed(self.buffer):
                if event.input_type == input_type and not event.consumed:
                    event.duration = duration
                    del self._hold_timers[input_type]
                    return event

        return None

    def get_oldest(self, unconsumed_only: bool = True) -> Optional[InputEvent]:
        """
        Get oldest input event.

        Args:
            unconsumed_only: Only return unconsumed events

        Returns:
            Oldest input event or None
        """
        for event in self.buffer:
            if not unconsumed_only or not event.consumed:
                return event
        return None

    def get_newest(self, unconsumed_only: bool = True) -> Optional[InputEvent]:
        """
        Get newest input event.

        Args:
            unconsumed_only: Only return unconsumed events

        Returns:
            Newest input event or None
        """
        for event in reversed(self.buffer):
            if not unconsumed_only or not event.consumed:
                return event
        return None

    def get_within_window(self, window_ms: Optional[int] = None) -> List[InputEvent]:
        """
        Get inputs within time window.

        Args:
            window_ms: Time window (uses config if None)

        Returns:
            List of input events
        """
        if window_ms is None:
            window_ms = self.config.buffer_window

        self._current_time = time.time() * 1000
        cutoff = self._current_time - window_ms

        return [event for event in self.buffer if event.timestamp >= cutoff and not event.consumed]

    def consume(self, input_type: InputType) -> bool:
        """
        Mark input as consumed.

        Args:
            input_type: Type of input to consume

        Returns:
            True if input was found and consumed
        """
        for event in self.buffer:
            if event.input_type == input_type and not event.consumed:
                event.consumed = True
                return True
        return False

    def consume_oldest(self) -> bool:
        """
        Consume oldest unconsumed input.

        Returns:
            True if input was consumed
        """
        event = self.get_oldest(unconsumed_only=True)
        if event:
            event.consumed = True
            return True
        return False

    def clear(self) -> None:
        """Clear all buffered inputs."""
        self.buffer.clear()
        self.combo_queue.clear()
        self._hold_timers.clear()

    def clear_old(self, max_age_ms: int = 500) -> None:
        """
        Clear old inputs.

        Args:
            max_age_ms: Maximum age in milliseconds
        """
        self._current_time = time.time() * 1000
        cutoff = self._current_time - max_age_ms

        # Remove old events
        while self.buffer and self.buffer[0].timestamp < cutoff:
            self.buffer.popleft()

    def is_held(self, input_type: InputType) -> bool:
        """
        Check if input is being held.

        Args:
            input_type: Type of input

        Returns:
            True if input is held
        """
        if input_type not in self._hold_timers:
            return False

        self._current_time = time.time() * 1000
        duration = self._current_time - self._hold_timers[input_type]

        return duration >= self.config.hold_threshold

    def get_combo_sequence(self, length: int = 3) -> List[InputType]:
        """
        Get recent combo sequence.

        Args:
            length: Number of inputs to return

        Returns:
            List of input types
        """
        sequence = [event.input_type for event in self.combo_queue]
        return sequence[-length:] if len(sequence) >= length else sequence

    def matches_combo(self, combo: List[InputType]) -> bool:
        """
        Check if recent inputs match combo.

        Args:
            combo: Combo sequence to match

        Returns:
            True if combo matched
        """
        sequence = self.get_combo_sequence(len(combo))
        return sequence == combo

    def get_count(self) -> int:
        """Get number of buffered inputs."""
        return len(self.buffer)

    def get_unconsumed_count(self) -> int:
        """Get number of unconsumed inputs."""
        return sum(1 for e in self.buffer if not e.consumed)


class InputManager:
    """
    Central input management system.
    
    Supports keyboard, gamepad, and mouse input.
    Includes input recording/playback for testing.

    Usage:
        input_mgr = InputManager()
        input_mgr.handle_event(event)
        input_mgr.update()
        jump_pressed = input_mgr.is_action_pressed(InputType.JUMP)
    """

    def __init__(self, config: Optional[InputConfig] = None) -> None:
        """
        Initialize input manager.

        Args:
            config: Input configuration
        """
        self.config = config or InputConfig()
        self.buffer = InputBuffer(self.config)

        # Key bindings
        self.key_bindings: Dict[int, InputType] = {}
        self._pressed_keys: set[int] = set()
        
        # Gamepad state
        self._gamepad_connected = False
        self._gamepad_axes: dict[int, float] = {}
        self._gamepad_buttons: dict[int, InputType] = {}
        
        # Mouse state
        self._mouse_buttons: dict[int, InputType] = {}
        self._mouse_position: tuple[int, int] = (0, 0)

        # State
        self.enabled = True
        self._current_time = 0.0
        
        # Input recording (for testing/replay)
        self._recording: list[tuple[float, InputEvent]] = []
        self._playback: list[tuple[float, InputEvent]] | None = None
        self._playback_start: float = 0.0

        # Callbacks
        self._on_input: Optional[Callable[[InputEvent], None]] = None

        self._setup_default_bindings()
        self._setup_gamepad_bindings()

    def _setup_default_bindings(self) -> None:
        """Setup default key bindings."""
        self.key_bindings = {
            pg.K_LEFT: InputType.MOVE_LEFT,
            pg.K_RIGHT: InputType.MOVE_RIGHT,
            pg.K_UP: InputType.MOVE_UP,
            pg.K_DOWN: InputType.MOVE_DOWN,
            pg.K_a: InputType.JUMP,
            pg.K_SPACE: InputType.JUMP,
            pg.K_s: InputType.ACTION,
            pg.K_LSHIFT: InputType.ACTION,
            pg.K_ESCAPE: InputType.PAUSE,
        }
        
    def _setup_gamepad_bindings(self) -> None:
        """Setup gamepad button bindings."""
        # Xbox/PlayStation style layout
        self._gamepad_buttons = {
            0: InputType.JUMP,       # A / Cross
            1: InputType.ACTION,     # B / Circle  
            2: InputType.ACTION,     # X / Square
            3: InputType.JUMP,       # Y / Triangle
            6: InputType.PAUSE,      # Start
            7: InputType.PAUSE,      # Back/Select
        }

    def set_binding(self, key: int, input_type: InputType) -> None:
        """
        Set key binding.

        Args:
            key: Pygame key code
            input_type: Input type
        """
        self.key_bindings[key] = input_type
        
    def set_gamepad_binding(self, button: int, input_type: InputType) -> None:
        """
        Set gamepad button binding.
        
        Args:
            button: Gamepad button index
            input_type: Input type
        """
        self._gamepad_buttons[button] = input_type

    def get_binding(self, key: int) -> Optional[InputType]:
        """Get input type for key."""
        return self.key_bindings.get(key)

    def handle_event(self, event: pg.event.Event) -> bool:
        """
        Handle pygame event.

        Args:
            event: Pygame event

        Returns:
            True if event was handled
        """
        if not self.enabled:
            return False

        if event.type == pg.KEYDOWN:
            if event.key in self.key_bindings:
                input_type = self.key_bindings[event.key]
                self.buffer.add(input_type)
                self._pressed_keys.add(event.key)

                if self._on_input:
                    self._on_input(self.buffer.get_newest())  # type: ignore

                return True

        elif event.type == pg.KEYUP:
            if event.key in self.key_bindings:
                input_type = self.key_bindings[event.key]
                self.buffer.release(input_type)
                self._pressed_keys.discard(event.key)
                return True
                
        elif event.type == pg.JOYBUTTONDOWN:
            if event.button in self._gamepad_buttons:
                input_type = self._gamepad_buttons[event.button]
                self.buffer.add(input_type)
                if self._on_input:
                    self._on_input(self.buffer.get_newest())  # type: ignore
                return True
                
        elif event.type == pg.JOYBUTTONUP:
            if event.button in self._gamepad_buttons:
                input_type = self._gamepad_buttons[event.button]
                self.buffer.release(input_type)
                return True
                
        elif event.type == pg.JOYAXISMOTION:
            self._gamepad_axes[event.axis] = event.value
            # Handle axis-based movement
            if event.axis in (0, 2):  # Left stick X or triggers
                if event.value < -self.config.deadzone:
                    self.buffer.add(InputType.MOVE_LEFT)
                elif event.value > self.config.deadzone:
                    self.buffer.add(InputType.MOVE_RIGHT)
                return True
                
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button in self._mouse_buttons:
                input_type = self._mouse_buttons[event.button]
                self.buffer.add(input_type, position=event.pos)
                return True
                
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button in self._mouse_buttons:
                input_type = self._mouse_buttons[event.button]
                self.buffer.release(input_type)
                return True
                
        elif event.type == pg.MOUSEMOTION:
            self._mouse_position = event.pos

        return False

    def update(self) -> None:
        """Update input state."""
        self._current_time = time.time() * 1000

        # Clear old inputs
        self.buffer.clear_old(self.config.buffer_window * 2)
        
        # Check gamepad connection
        if pg.joystick.get_count() > 0:
            if not self._gamepad_connected:
                try:
                    joy = pg.joystick.Joystick(0)
                    if not joy.get_init():
                        joy.init()
                    self._gamepad_connected = True
                except pg.error:
                    pass
                    
    def is_gamepad_connected(self) -> bool:
        """Check if gamepad is connected."""
        return self._gamepad_connected

    def is_action_pressed(self, input_type: InputType) -> bool:
        """
        Check if action is currently pressed.

        Args:
            input_type: Input type

        Returns:
            True if action is pressed
        """
        events = self.buffer.get_within_window(self.config.buffer_window)
        return any(e.input_type == input_type and not e.consumed for e in events)

    def is_action_held(self, input_type: InputType) -> bool:
        """
        Check if action is being held.

        Args:
            input_type: Input type

        Returns:
            True if action is held
        """
        return self.buffer.is_held(input_type)

    def consume_action(self, input_type: InputType) -> bool:
        """
        Consume action input.

        Args:
            input_type: Input type

        Returns:
            True if input was consumed
        """
        return self.buffer.consume(input_type)

    def get_direction(self) -> tuple[int, int]:
        """
        Get current movement direction.

        Returns:
            (x, y) direction (-1, 0, 1)
        """
        x = 0
        y = 0

        events = self.buffer.get_within_window(100)
        
        # Check gamepad axes first
        if self._gamepad_connected:
            for axis, value in self._gamepad_axes.items():
                if axis == 0:  # Left stick X
                    if abs(value) > self.config.deadzone:
                        x = 1 if value > 0 else -1
                        break

        # Fall back to keyboard
        if x == 0 and y == 0:
            for event in events:
                if event.consumed:
                    continue

                if event.input_type == InputType.MOVE_LEFT:
                    x = -1
                elif event.input_type == InputType.MOVE_RIGHT:
                    x = 1
                elif event.input_type == InputType.MOVE_UP:
                    y = -1
                elif event.input_type == InputType.MOVE_DOWN:
                    y = 1

        return (x, y)

    def get_combo_sequence(self, length: int = 5) -> List[InputType]:
        """Get recent combo sequence."""
        return self.buffer.get_combo_sequence(length)

    def matches_combo(self, combo: List[InputType]) -> bool:
        """Check if recent inputs match combo."""
        return self.buffer.matches_combo(combo)

    def set_on_input(self, callback: Callable[[InputEvent], None]) -> None:
        """Set input callback."""
        self._on_input = callback

    def reset(self) -> None:
        """Reset input state."""
        self.buffer.clear()
        self._pressed_keys.clear()
        self._gamepad_axes.clear()
        
    def start_recording(self) -> None:
        """Start recording input sequence."""
        self._recording.clear()
        self._playback_start = time.time() * 1000
        
    def stop_recording(self) -> list[tuple[float, InputEvent]]:
        """Stop recording and return sequence."""
        return self._recording.copy()
        
    def enable_recording_mode(self) -> None:
        """Enable automatic recording mode."""
        def on_input(event: InputEvent) -> None:
            current_time = time.time() * 1000
            self._recording.append((current_time - self._playback_start, event))
        self.set_on_input(on_input)
        
    def start_playback(self, recording: list[tuple[float, InputEvent]]) -> None:
        """Start playback of recorded input."""
        self._playback = recording.copy()
        self._playback_index = 0
        self._playback_start = time.time() * 1000
        
    def update_playback(self) -> None:
        """Update playback state - call each frame."""
        if self._playback is None:
            return
            
        current_time = time.time() * 1000 - self._playback_start
        
        while self._playback_index < len(self._playback):
            event_time, event = self._playback[self._playback_index]
            if event_time <= current_time:
                self.buffer.add(event.input_type)
                self._playback_index += 1
            else:
                break
                
    def is_playback_complete(self) -> bool:
        """Check if playback is complete."""
        return self._playback is not None and self._playback_index >= len(self._playback)


class ComboDetector:
    """
    Detects input combos.

    Usage:
        detector = ComboDetector(input_manager)
        detector.register_combo("jump_attack", [JUMP, ACTION])
        if detector.check_combos():
            # Combo detected
    """

    def __init__(self, input_manager: InputManager) -> None:
        """
        Initialize combo detector.

        Args:
            input_manager: Input manager instance
        """
        self.input_manager = input_manager
        self.combos: Dict[str, List[InputType]] = {}
        self.callbacks: Dict[str, Callable[[], None]] = {}
        self.cooldowns: Dict[str, float] = {}
        self.last_triggered: Dict[str, float] = {}

    def register_combo(
        self, name: str, sequence: List[InputType], callback: Optional[Callable[[], None]] = None, cooldown: int = 500
    ) -> None:
        """
        Register a combo.

        Args:
            name: Combo name
            sequence: Input sequence
            callback: Function to call on combo
            cooldown: Cooldown in milliseconds
        """
        self.combos[name] = sequence
        if callback:
            self.callbacks[name] = callback
        self.cooldowns[name] = cooldown
        self.last_triggered[name] = 0

    def check_combos(self) -> Optional[str]:
        """
        Check for combo matches.

        Returns:
            Name of matched combo or None
        """
        self._current_time = time.time() * 1000

        for name, sequence in self.combos.items():
            # Check cooldown
            if self._current_time - self.last_triggered[name] < self.cooldowns[name]:
                continue

            # Check combo
            if self.input_manager.matches_combo(sequence):
                self.last_triggered[name] = self._current_time

                # Trigger callback
                if name in self.callbacks:
                    self.callbacks[name]()

                return name

        return None

    def reset(self) -> None:
        """Reset combo detector."""
        # clear any history; combos may be re-registered later if needed
        self.last_triggered.clear()


# Default Mario combos
MARIO_COMBOS = {
    "jump_attack": ([InputType.JUMP, InputType.ACTION], "Jump attack combo"),
    "run_jump": ([InputType.MOVE_RIGHT, InputType.JUMP], "Running jump"),
    "backflip": ([InputType.MOVE_LEFT, InputType.JUMP], "Backflip"),
    "ground_pound": ([InputType.JUMP, InputType.MOVE_DOWN], "Ground pound"),
}


def create_mario_combos(input_manager: InputManager) -> ComboDetector:
    """
    Create combo detector with default Mario combos.

    Args:
        input_manager: Input manager instance

    Returns:
        Configured ComboDetector
    """
    detector = ComboDetector(input_manager)

    for name, (sequence, _) in MARIO_COMBOS.items():
        detector.register_combo(name, sequence)

    return detector
