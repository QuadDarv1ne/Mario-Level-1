"""
Advanced Particle Effects for Super Mario Bros.

Extended particle system with:
- Enhanced particle types (jump dust, landing, shell sparks)
- Object pooling for performance
- Combo visual effects
- Weather particles integration
- Batch rendering for improved performance
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple, Dict, Any

import pygame as pg


class AdvancedParticleType(Enum):
    """Advanced particle types."""

    JUMP_DUST = auto()
    LANDING_DUST = auto()
    SHELL_SPARK = auto()
    FIREBALL_TRAIL = auto()
    STAR_TRAIL = auto()
    COIN_BURST = auto()
    MUSHROOM_SPORES = auto()
    WATER_SPLASH = auto()
    FLAG_SHINE = auto()
    COMBO_STAR = auto()


@dataclass
class AdvancedParticle:
    """Advanced particle with more features."""

    x: float
    y: float
    vx: float
    vy: float
    lifetime: float  # ms
    birth_time: float
    color: Tuple[int, int, int]
    size: float
    gravity: float = 0.0
    particle_type: AdvancedParticleType = AdvancedParticleType.JUMP_DUST
    rotation: float = 0.0
    rotation_speed: float = 0.0
    scale: float = 1.0

    @property
    def age(self) -> float:
        """Get particle age in ms."""
        return time.time() * 1000 - self.birth_time

    @property
    def is_alive(self) -> bool:
        """Check if particle is alive."""
        return self.age < self.lifetime

    @property
    def life_progress(self) -> float:
        """Get life progress (0.0 to 1.0)."""
        return min(1.0, self.age / self.lifetime)


class AdvancedParticleSystem:
    """
    Advanced particle system with object pooling.

    Features:
    - Object pooling for better performance
    - Multiple particle types
    - Combo visual effects
    - Weather integration
    """

    # Particle templates
    TEMPLATES: Dict[str, Dict[str, Any]] = {
        "jump_dust": {
            "color": (180, 180, 180),
            "size_range": (3, 6),
            "speed_range": (1, 2),
            "lifetime_range": (200, 400),
            "count": (3, 6),
            "gravity": 0,
            "spread": 120,
        },
        "landing_dust": {
            "color": (160, 160, 160),
            "size_range": (2, 5),
            "speed_range": (2, 4),
            "lifetime_range": (150, 300),
            "count": (5, 8),
            "gravity": 0.05,
            "spread": 180,
        },
        "shell_spark": {
            "color": (255, 200, 50),
            "size_range": (2, 4),
            "speed_range": (4, 8),
            "lifetime_range": (100, 250),
            "count": (5, 10),
            "gravity": 0.3,
            "spread": 90,
        },
        "fireball_trail": {
            "color": (255, 100, 50),
            "size_range": (2, 4),
            "speed_range": (0.5, 1),
            "lifetime_range": (100, 200),
            "count": (2, 4),
            "gravity": -0.1,
            "spread": 30,
        },
        "star_trail": {
            "color": (255, 255, 200),
            "size_range": (2, 3),
            "speed_range": (1, 2),
            "lifetime_range": (150, 300),
            "count": (3, 6),
            "gravity": -0.05,
            "spread": 60,
        },
        "coin_burst": {
            "color": (255, 215, 0),
            "size_range": (3, 5),
            "speed_range": (2, 5),
            "lifetime_range": (400, 700),
            "count": (10, 15),
            "gravity": 0.2,
            "spread": 360,
        },
        "mushroom_spores": {
            "color": (255, 100, 100),
            "size_range": (2, 4),
            "speed_range": (0.5, 1.5),
            "lifetime_range": (800, 1500),
            "count": (8, 12),
            "gravity": -0.02,
            "spread": 180,
        },
        "water_splash": {
            "color": (100, 150, 255),
            "size_range": (2, 5),
            "speed_range": (2, 5),
            "lifetime_range": (300, 600),
            "count": (8, 15),
            "gravity": 0.3,
            "spread": 120,
        },
        "flag_shine": {
            "color": (255, 255, 200),
            "size_range": (3, 6),
            "speed_range": (1, 3),
            "lifetime_range": (500, 1000),
            "count": (10, 20),
            "gravity": -0.1,
            "spread": 360,
        },
        "combo_star": {
            "color": (255, 215, 0),
            "size_range": (4, 8),
            "speed_range": (3, 6),
            "lifetime_range": (600, 1000),
            "count": (15, 25),
            "gravity": 0.15,
            "spread": 360,
        },
    }

    def __init__(self, max_particles: int = 1000, pool_size: int = 200) -> None:
        """
        Initialize advanced particle system.

        Args:
            max_particles: Maximum active particles
            pool_size: Initial object pool size
        """
        self.max_particles = max_particles
        self.particles: List[AdvancedParticle] = []

        # Object pool
        self._pool: List[AdvancedParticle] = []
        self._initialize_pool(pool_size)

        # Statistics
        self.stats = {
            "emitted": 0,
            "recycled": 0,
            "active": 0,
        }

    def _initialize_pool(self, size: int) -> None:
        """Initialize object pool."""
        for _ in range(size):
            self._pool.append(self._create_empty_particle())

    def _create_empty_particle(self) -> AdvancedParticle:
        """Create empty particle for pooling."""
        return AdvancedParticle(x=0, y=0, vx=0, vy=0, lifetime=0, birth_time=0, color=(0, 0, 0), size=0)

    def emit(self, x: float, y: float, particle_type: str, count_override: Optional[int] = None) -> int:
        """
        Emit particles at position.

        Args:
            x, y: Emission position
            particle_type: Type from TEMPLATES
            count_override: Override template count

        Returns:
            Number of particles emitted
        """
        if particle_type not in self.TEMPLATES:
            return 0

        template = self.TEMPLATES[particle_type]

        # Determine count
        if count_override:
            count = count_override
        else:
            min_count, max_count = template["count"]
            count = random.randint(min_count, max_count)

        # Limit by max_particles
        if len(self.particles) + count > self.max_particles:
            count = max(0, self.max_particles - len(self.particles))

        emitted = 0
        current_time = time.time() * 1000

        for _ in range(count):
            particle = self._get_pooled_particle()
            if not particle:
                break

            self._setup_particle(particle, x, y, template, current_time)
            self.particles.append(particle)
            emitted += 1

        self.stats["emitted"] += emitted
        return emitted

    def _get_pooled_particle(self) -> Optional[AdvancedParticle]:
        """Get particle from pool or create new."""
        if self._pool:
            self.stats["recycled"] += 1
            return self._pool.pop()

        # Pool exhausted, create new
        return self._create_empty_particle()

    def _setup_particle(
        self, particle: AdvancedParticle, x: float, y: float, template: Dict[str, Any], current_time: float
    ) -> None:
        """Setup particle from template."""
        particle.x = x
        particle.y = y

        # Random velocity with spread
        spread = template["spread"]
        angle = random.uniform(0, spread)
        speed = random.uniform(*template["speed_range"])

        particle.vx = speed * math.cos(math.radians(angle))
        particle.vy = speed * math.sin(math.radians(angle))

        # Other properties
        particle.lifetime = random.uniform(*template["lifetime_range"])
        particle.birth_time = current_time
        particle.color = template["color"]
        particle.size = random.uniform(*template["size_range"])
        particle.gravity = template["gravity"]
        particle.rotation = random.uniform(0, 360)
        particle.rotation_speed = random.uniform(-10, 10)
        particle.scale = 1.0
        particle.particle_type = AdvancedParticleType.JUMP_DUST

    def update(self, dt: float) -> None:
        """
        Update all particles.

        Args:
            dt: Delta time in ms
        """
        alive_particles = []
        current_time = time.time() * 1000

        for particle in self.particles:
            # Inline age calculation for performance
            age = current_time - particle.birth_time
            if age < particle.lifetime:
                # Update physics
                particle.vy += particle.gravity
                particle.x += particle.vx
                particle.y += particle.vy
                particle.rotation += particle.rotation_speed
                particle.scale = 1.0 - (age / particle.lifetime) * 0.5
                alive_particles.append(particle)
            else:
                # Return to pool
                self._pool.append(particle)

        self.particles = alive_particles
        self.stats["active"] = len(self.particles)

    def clear(self) -> None:
        """Clear all particles."""
        self._pool.extend(self.particles)
        self.particles.clear()
        self.stats["active"] = 0

    def get_stats(self) -> Dict[str, int]:
        """Get particle system statistics."""
        return self.stats.copy()

    def draw_batch(self, surface: pg.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """
        Draw all particles using batch rendering.

        Uses a single surface for all particles to reduce draw calls.

        Args:
            surface: Surface to draw to
            camera_offset: Camera offset (x, y)
        """
        if not self.particles:
            return

        cam_x, cam_y = camera_offset

        # Create temporary surface for batching
        temp_surface = pg.Surface((surface.get_width(), surface.get_height()), pg.SRCALPHA)

        for particle in self.particles:
            self._draw_particle_batched(temp_surface, particle, cam_x, cam_y)

        surface.blit(temp_surface, (0, 0))

    def _draw_particle_batched(self, surface: pg.Surface, particle: AdvancedParticle, cam_x: int, cam_y: int) -> None:
        """Draw single particle on batched surface."""
        screen_x = int(particle.x - cam_x)
        screen_y = int(particle.y - cam_y)

        # Skip if off-screen
        if (
            screen_x < -50
            or screen_x > surface.get_width() + 50
            or screen_y < -50
            or screen_y > surface.get_height() + 50
        ):
            return

        alpha = int(255 * (1 - particle.life_progress))
        size = max(1, int(particle.size * particle.scale))

        color_with_alpha = (*particle.color, alpha)

        if particle.particle_type == AdvancedParticleType.COMBO_STAR:
            self._draw_star(surface, color_with_alpha, screen_x, screen_y, size)
        else:
            pg.draw.circle(surface, color_with_alpha, (screen_x + size // 2, screen_y + size // 2), size // 2)

    def _draw_star(self, surface: pg.Surface, color: Tuple[int, int, int], x: int, y: int, size: int) -> None:
        """Draw star shape for combo particles."""
        points = []
        center_x, center_y = x + size // 2, y + size // 2
        outer_r = size // 2
        inner_r = size // 4

        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = outer_r if i % 2 == 0 else inner_r
            px = center_x + r * math.cos(angle)
            py = center_y + r * math.sin(angle)
            points.append((px, py))

        pg.draw.polygon(surface, color, points)
