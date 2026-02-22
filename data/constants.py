"""
Game constants and configuration values.

This module contains all magic numbers and string constants used throughout
the game, organized by category for easy reference and modification.
"""
from __future__ import annotations

__author__ = 'justinarmstrong'

# =============================================================================
# SCREEN SETTINGS
# =============================================================================
SCREEN_HEIGHT: int = 600
SCREEN_WIDTH: int = 800
SCREEN_SIZE: tuple[int, int] = (SCREEN_WIDTH, SCREEN_HEIGHT)
ORIGINAL_CAPTION: str = "Super Mario Bros 1-1"

# =============================================================================
# COLORS
# Format: (Red, Green, Blue) - each value 0-255
# =============================================================================
GRAY: tuple[int, int, int] = (100, 100, 100)
NAVYBLUE: tuple[int, int, int] = (60, 60, 100)
WHITE: tuple[int, int, int] = (255, 255, 255)
RED: tuple[int, int, int] = (255, 0, 0)
GREEN: tuple[int, int, int] = (0, 255, 0)
FOREST_GREEN: tuple[int, int, int] = (31, 162, 35)
BLUE: tuple[int, int, int] = (0, 0, 255)
SKY_BLUE: tuple[int, int, int] = (39, 145, 251)
YELLOW: tuple[int, int, int] = (255, 255, 0)
ORANGE: tuple[int, int, int] = (255, 128, 0)
PURPLE: tuple[int, int, int] = (255, 0, 255)
CYAN: tuple[int, int, int] = (0, 255, 255)
BLACK: tuple[int, int, int] = (0, 0, 0)
NEAR_BLACK: tuple[int, int, int] = (19, 15, 48)
COMBLUE: tuple[int, int, int] = (233, 232, 255)
GOLD: tuple[int, int, int] = (255, 215, 0)

BGCOLOR: tuple[int, int, int] = WHITE

# =============================================================================
# SCALE MULTIPLIERS
# Used to scale up sprites from their original pixel art size
# =============================================================================
SIZE_MULTIPLIER: float = 2.5
BRICK_SIZE_MULTIPLIER: float = 2.69
BACKGROUND_MULTIPLIER: float = 2.679
GROUND_HEIGHT: int = SCREEN_HEIGHT - 62

# =============================================================================
# MARIO PHYSICS & MOVEMENT
# =============================================================================
# Acceleration values
WALK_ACCEL: float = 0.15
RUN_ACCEL: float = 20.0
SMALL_TURNAROUND: float = 0.35

# Gravity and jumping
GRAVITY: float = 1.01
JUMP_GRAVITY: float = 0.31
JUMP_VEL: float = -10.0
FAST_JUMP_VEL: float = -12.5
MAX_Y_VEL: float = 11.0

# Maximum speeds (pixels per frame)
MAX_RUN_SPEED: float = 800.0
MAX_WALK_SPEED: float = 6.0

# =============================================================================
# MARIO STATES
# String constants for Mario's animation/behavior state machine
# =============================================================================
STAND: str = 'standing'
WALK: str = 'walk'
JUMP: str = 'jump'
FALL: str = 'fall'
SMALL_TO_BIG: str = 'small to big'
BIG_TO_FIRE: str = 'big to fire'
BIG_TO_SMALL: str = 'big to small'
FLAGPOLE: str = 'flag pole'
WALKING_TO_CASTLE: str = 'walking to castle'
END_OF_LEVEL_FALL: str = 'end of level fall'
DEATH_JUMP: str = 'death jump'
BOTTOM_OF_POLE: str = 'bottom of pole'

# =============================================================================
# ENEMY STATES (GOOMBA)
# =============================================================================
LEFT: str = 'left'
RIGHT: str = 'right'
JUMPED_ON: str = 'jumped on'
DEATH_JUMP: str = 'death jump'

# =============================================================================
# KOOPA STATES
# =============================================================================
SHELL_SLIDE: str = 'shell slide'

# =============================================================================
# BRICK STATES
# =============================================================================
RESTING: str = 'resting'
BUMPED: str = 'bumped'

# =============================================================================
# COIN STATES
# =============================================================================
OPENED: str = 'opened'
SPIN: str = 'spin'

# =============================================================================
# MUSHROOM STATES
# =============================================================================
REVEAL: str = 'reveal'
SLIDE: str = 'slide'

# =============================================================================
# STAR STATES
# =============================================================================
BOUNCE: str = 'bounce'

# =============================================================================
# FIRE STATES
# =============================================================================
FLYING: str = 'flying'
BOUNCING: str = 'bouncing'
EXPLODING: str = 'exploding'

# =============================================================================
# BRICK AND COIN BOX CONTENTS
# =============================================================================
MUSHROOM: str = 'mushroom'
STAR: str = 'star'
FIREFLOWER: str = 'fireflower'
SIXCOINS: str = '6coins'
COIN: str = 'coin'
LIFE_MUSHROOM: str = '1up_mushroom'
FIREBALL: str = 'fireball'

# =============================================================================
# ENEMY TYPES
# =============================================================================
GOOMBA: str = 'goomba'
KOOPA: str = 'koopa'

# =============================================================================
# LEVEL STATES
# =============================================================================
FROZEN: str = 'frozen'
NOT_FROZEN: str = 'not frozen'
IN_CASTLE: str = 'in castle'
FLAG_AND_FIREWORKS: str = 'flag and fireworks'

# =============================================================================
# FLAG STATES
# =============================================================================
TOP_OF_POLE: str = 'top of pole'
SLIDE_DOWN: str = 'slide down'
BOTTOM_OF_POLE: str = 'bottom of pole'

# =============================================================================
# SCORE VALUES
# =============================================================================
ONEUP: str = '379'  # 1UP score display value

# =============================================================================
# MAIN MENU STATES
# =============================================================================
PLAYER1: str = '1 player'
PLAYER2: str = '2 player'

# =============================================================================
# OVERHEAD INFO STATES
# =============================================================================
MAIN_MENU: str = 'main menu'
LOAD_SCREEN: str = 'loading screen'
LEVEL: str = 'level'
GAME_OVER: str = 'game over'
FAST_COUNT_DOWN: str = 'fast count down'
END_OF_LEVEL: str = 'end of level'

# =============================================================================
# GAME INFO DICTIONARY KEYS
# =============================================================================
COIN_TOTAL: str = 'coin total'
SCORE: str = 'score'
TOP_SCORE: str = 'top score'
LIVES: str = 'lives'
CURRENT_TIME: str = 'current time'
LEVEL_STATE: str = 'level state'
CAMERA_START_X: str = 'camera start x'
MARIO_DEAD: str = 'mario dead'

# =============================================================================
# GLOBAL GAME STATES
# States for the entire game state machine
# =============================================================================
MAIN_MENU: str = 'main menu'
LOAD_SCREEN: str = 'load screen'
TIME_OUT: str = 'time out'
GAME_OVER: str = 'game over'
LEVEL1: str = 'level1'

# =============================================================================
# SOUND STATES
# =============================================================================
NORMAL: str = 'normal'
STAGE_CLEAR: str = 'stage clear'
WORLD_CLEAR: str = 'world clear'
TIME_WARNING: str = 'time warning'
SPED_UP_NORMAL: str = 'sped up normal'
MARIO_INVINCIBLE: str = 'mario invincible'

# =============================================================================
# TIMING CONSTANTS (milliseconds)
# =============================================================================
ENEMY_ANIMATION_INTERVAL: int = 125  # Enemy frame switch timing
GOOMBA_DEATH_DELAY: int = 500  # Delay before goomba disappears after being stomped
FIREBALL_INTERVAL: int = 200  # Minimum time between fireball shots
INVINCIBLE_DURATION: int = 2000  # Duration of star power invincibility
HURT_INVINCIBLE_DURATION: int = 1000  # Duration of invincibility after getting hurt
FLAG_SLIDE_DURATION: int = 1000  # Duration of flag slide animation

# =============================================================================
# SCORE VALUES
# =============================================================================
SCORE_GOOMBA_STOMP: int = 100
SCORE_KOOPA_STOMP: int = 100
SCORE_STAR: int = 1000
SCORE_MUSHROOM: int = 1000
SCORE_1UP: int = 100
SCORE_FLAG_POLE_LOW: int = 100
SCORE_FLAG_POLE_MID: int = 400
SCORE_FLAG_POLE_HIGH: int = 800
SCORE_FLAG_POLE_HIGHER: int = 2000
SCORE_FLAG_POLE_TOP: int = 5000