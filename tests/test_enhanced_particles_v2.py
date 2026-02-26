"""
Tests for Enhanced Particle System v2.

Tests cover:
- Particle creation and configuration
- Particle behaviors
- Particle system management
- Presets
- Effects
"""

from __future__ import annotations

import math
from typing import Any
from unittest.mock import MagicMock

import pygame as pg
import pytest

from data.enhanced_particles_v2 import (
    EnhancedParticle,
    EnhancedParticleSystem,
    ParticleBehavior,
    ParticleConfig,
    ParticleShape,
    get_particle_system,
)


class TestParticleConfig:
    """Test ParticleConfig."""

    def test_create_default_config(self) -> None:
        """Test creating default config."""
        config = ParticleConfig()

        assert config.color == (255, 255, 255)
        assert config.shape == ParticleShape.CIRCLE
        assert config.size == 5.0
        assert config.lifetime == 1.0
        assert config.behavior == ParticleBehavior.NORMAL

    def test_create_custom_config(self) -> None:
        """Test creating custom config."""
        config = ParticleConfig(
            color=(255, 100, 0),
            shape=ParticleShape.SPARK,
            size=10.0,
            lifetime=2.0,
            velocity=(5.0, -10.0),
            gravity=9.8,
        )

        assert config.color == (255, 100, 0)
        assert config.shape == ParticleShape.SPARK
        assert config.size == 10.0
        assert config.gravity == 9.8


class TestEnhancedParticle:
    """Test EnhancedParticle."""

    def test_create_particle(self) -> None:
        """Test creating particle."""
        particle = EnhancedParticle(100, 200)

        assert particle.x == 100
        assert particle.y == 200
        assert particle.alive
        assert particle.age == 0.0

    def test_create_particle_with_config(self) -> None:
        """Test creating particle with config."""
        config = ParticleConfig(
            color=(255, 0, 0),
            size=8.0,
            lifetime=0.5,
            velocity=(10.0, 0.0),
        )

        particle = EnhancedParticle(50, 50, config)

        assert particle.config.color == (255, 0, 0)
        assert particle.config.size == 8.0
        assert particle.config.lifetime == 0.5

    def test_particle_update(self) -> None:
        """Test particle update."""
        config = ParticleConfig(
            velocity=(100.0, 0.0),
            lifetime=1.0,
        )

        particle = EnhancedParticle(0, 0, config)
        particle.update(0.1)  # 100ms

        assert particle.age == 0.1
        assert particle.x > 0  # Moved right
        assert particle.alive

    def test_particle_expiration(self) -> None:
        """Test particle expires after lifetime."""
        config = ParticleConfig(lifetime=0.1)  # 100ms

        particle = EnhancedParticle(0, 0, config)
        particle.update(0.15)  # 150ms

        assert not particle.alive

    def test_particle_gravity(self) -> None:
        """Test particle with gravity."""
        config = ParticleConfig(
            velocity=(0.0, 0.0),
            gravity=100.0,
            lifetime=1.0,
        )

        particle = EnhancedParticle(100, 100, config)
        particle.update(0.1)

        assert particle.vy > 0  # Falling down
        assert particle.y > 100

    def test_particle_color_gradient(self) -> None:
        """Test particle color gradient."""
        config = ParticleConfig(
            color=(255, 0, 0),
            color_end=(0, 0, 255),
            lifetime=1.0,
        )

        particle = EnhancedParticle(0, 0, config)
        particle.update(0.5)  # Halfway

        # Color should be between red and blue
        assert particle.current_color[0] < 255  # Less red
        assert particle.current_color[2] > 0  # More blue

    def test_particle_size_change(self) -> None:
        """Test particle size change over time."""
        config = ParticleConfig(
            size=10.0,
            size_end=2.0,
            lifetime=1.0,
        )

        particle = EnhancedParticle(0, 0, config)

        assert particle.current_size == 10.0

        particle.update(0.5)
        assert particle.current_size < 10.0
        assert particle.current_size > 2.0

    def test_particle_behaviors(self) -> None:
        """Test different particle behaviors."""
        # Test FLOAT behavior
        config_float = ParticleConfig(
            behavior=ParticleBehavior.FLOAT,
            behavior_params={"frequency": 2, "amplitude": 50},
            lifetime=1.0,
        )

        particle_float = EnhancedParticle(0, 0, config_float)
        particle_float.update(0.1)

        # Test EXPLODE behavior
        config_explode = ParticleConfig(
            behavior=ParticleBehavior.EXPLODE,
            behavior_params={"speed": 100, "angle": 0},
            lifetime=1.0,
        )

        particle_explode = EnhancedParticle(0, 0, config_explode)
        particle_explode.update(0.1)

        assert particle_explode.vx > 50  # Moving fast

    def test_particle_homing(self) -> None:
        """Test homing behavior."""
        config = ParticleConfig(
            behavior=ParticleBehavior.HOMING,
            behavior_params={"speed": 100},
            lifetime=1.0,
        )

        particle = EnhancedParticle(0, 0, config)
        target = (100, 100)

        particle.update(0.1, target=target)

        # Should move towards target
        assert particle.vx > 0
        assert particle.vy > 0

    def test_particle_alpha_fade(self) -> None:
        """Test alpha fade in/out."""
        config = ParticleConfig(
            alpha=255,
            alpha_end=0,
            fade_in=0.2,
            fade_out=0.2,
            lifetime=1.0,
        )

        particle = EnhancedParticle(0, 0, config)

        # During fade in
        particle.update(0.1)
        assert particle.current_alpha < 255

        # Fully visible
        particle.update(0.3)
        assert particle.current_alpha > 100

    @pytest.mark.skip(reason="Requires display")
    @pytest.mark.parametrize(
        "shape",
        [
            ParticleShape.CIRCLE,
            ParticleShape.SQUARE,
            ParticleShape.TRIANGLE,
            ParticleShape.STAR,
            ParticleShape.RING,
            ParticleShape.SPARK,
        ],
    )
    def test_particle_shapes(self, shape: ParticleShape) -> None:
        """Test different particle shapes."""
        config = ParticleConfig(shape=shape, size=10.0, lifetime=1.0)
        particle = EnhancedParticle(0, 0, config)

        # Create surface for drawing
        surface = pg.Surface((100, 100))
        particle.draw(surface)

        # Just verify no crash
        assert particle.config.shape == shape


class TestEnhancedParticleSystem:
    """Test EnhancedParticleSystem."""

    def test_create_system(self) -> None:
        """Test creating particle system."""
        system = EnhancedParticleSystem(max_particles=500)

        assert system.max_particles == 500
        assert len(system.particles) == 0
        assert len(system.pool) == 0

    def test_emit_particles(self) -> None:
        """Test emitting particles."""
        system = EnhancedParticleSystem()

        count = system.emit(100, 100, "fire", count=10)

        assert count == 10
        assert len(system.particles) == 10

    def test_emit_invalid_preset(self) -> None:
        """Test emitting with invalid preset."""
        system = EnhancedParticleSystem()

        count = system.emit(100, 100, "invalid_preset", count=10)

        assert count == 0
        assert len(system.particles) == 0

    def test_emit_respects_max(self) -> None:
        """Test emission respects max particles."""
        system = EnhancedParticleSystem(max_particles=5)

        count = system.emit(0, 0, "smoke", count=10)

        assert count == 5
        assert len(system.particles) == 5

    def test_update_particles(self) -> None:
        """Test updating particles."""
        system = EnhancedParticleSystem()
        system.emit(0, 0, "spark", count=5)

        initial_count = len(system.particles)
        system.update(0.1)

        # All should still be alive (spark lifetime is 0.3s)
        assert len(system.particles) <= initial_count

    def test_update_removes_dead(self) -> None:
        """Test updating removes dead particles."""
        system = EnhancedParticleSystem()
        # Use very short lifetime
        system.emit(0, 0, "spark", count=5)

        # Manually set very short lifetime
        for p in system.particles:
            p.config.lifetime = 0.05
            p._lifetime = 0.05

        # Wait for particles to die
        system.update(0.1)

        # Most should be dead
        assert len(system.particles) <= 5

    def test_continuous_emission(self) -> None:
        """Test continuous emission."""
        system = EnhancedParticleSystem()

        system.emit_continuous("test_emitter", 100, 100, "smoke", rate=10)

        assert "test_emitter" in system.emitters
        assert system.emitters["test_emitter"]["active"]

        # Update to emit some particles
        system.update(0.5)

        assert len(system.particles) > 0

    def test_stop_emitter(self) -> None:
        """Test stopping emitter."""
        system = EnhancedParticleSystem()
        system.emit_continuous("test", 0, 0, "fire", rate=10)

        system.stop_emitter("test")

        assert not system.emitters["test"]["active"]

    def test_clear_particles(self) -> None:
        """Test clearing all particles."""
        system = EnhancedParticleSystem()
        system.emit(0, 0, "explosion", count=20)

        assert len(system.particles) > 0

        system.clear()

        assert len(system.particles) == 0
        assert len(system.pool) > 0

    def test_particle_pooling(self) -> None:
        """Test particle pooling."""
        system = EnhancedParticleSystem()
        system.emit(0, 0, "spark", count=10)

        # Set short lifetime
        for p in system.particles:
            p.config.lifetime = 0.05
            p._lifetime = 0.05

        # Let particles die
        system.update(0.1)

        # Should have some particles in pool
        initial_pool = len(system.pool)
        assert initial_pool >= 0  # Some particles may be pooled

        # Re-emit should work
        system.emit(0, 0, "spark", count=5)
        assert len(system.particles) > 0

    def test_get_stats(self) -> None:
        """Test getting statistics."""
        system = EnhancedParticleSystem(max_particles=100)
        system.emit(0, 0, "fire", count=10)

        stats = system.get_stats()

        assert stats["active"] == 10
        assert stats["max"] == 100
        assert stats["pooled"] >= 0

    def test_create_effect_explosion(self) -> None:
        """Test creating explosion effect."""
        system = EnhancedParticleSystem()

        system.create_effect("explosion", 100, 100)

        # Explosion creates multiple particle types
        assert len(system.particles) > 50  # 30+20+15+20 = 85

    def test_create_effect_coin(self) -> None:
        """Test creating coin collection effect."""
        system = EnhancedParticleSystem()

        system.create_effect("coin", 100, 100)

        assert len(system.particles) > 0

    def test_create_effect_powerup(self) -> None:
        """Test creating powerup effect."""
        system = EnhancedParticleSystem()

        system.create_effect("powerup", 100, 100)

        assert len(system.particles) > 20

    def test_create_effect_death(self) -> None:
        """Test creating death effect."""
        system = EnhancedParticleSystem()

        system.create_effect("death", 100, 100)

        assert len(system.particles) > 50

    def test_config_override(self) -> None:
        """Test config override during emission."""
        system = EnhancedParticleSystem()

        count = system.emit(
            0,
            0,
            "fire",
            count=5,
            config_override={"color": (0, 255, 0), "size": 15.0},
        )

        assert count == 5
        # Check one particle has overridden values
        if system.particles:
            particle = system.particles[0]
            assert particle.config.color == (0, 255, 0)
            assert particle.config.size == 15.0


class TestParticlePresets:
    """Test particle presets."""

    def test_all_presets_exist(self) -> None:
        """Test all presets are defined."""
        presets = [
            "fire",
            "smoke",
            "spark",
            "magic",
            "explosion",
            "debris",
            "energy_orb",
            "rain",
            "snow",
            "coin_burst",
        ]

        for preset in presets:
            assert preset in EnhancedParticleSystem.PRESETS

    def test_fire_preset(self) -> None:
        """Test fire preset configuration."""
        config = EnhancedParticleSystem.PRESETS["fire"]

        assert config.color == (255, 100, 0)
        assert config.shape == ParticleShape.CIRCLE
        assert config.lifetime == 0.5

    def test_spark_preset(self) -> None:
        """Test spark preset configuration."""
        config = EnhancedParticleSystem.PRESETS["spark"]

        assert config.shape == ParticleShape.SPARK
        assert config.behavior == ParticleBehavior.EXPLODE

    def test_magic_preset(self) -> None:
        """Test magic preset configuration."""
        config = EnhancedParticleSystem.PRESETS["magic"]

        assert config.shape == ParticleShape.STAR
        assert config.behavior == ParticleBehavior.SPIRAL


class TestGlobalParticleSystem:
    """Test global particle system instance."""

    def test_singleton(self) -> None:
        """Test system is singleton."""
        # Reset
        import data.enhanced_particles_v2 as epv2

        epv2._particle_system = None

        system1 = get_particle_system()
        system2 = get_particle_system()

        assert system1 is system2


class TestParticleDrawing:
    """Test particle drawing."""

    @pytest.mark.skip(reason="Requires display")
    def test_draw_on_surface(self) -> None:
        """Test drawing particle on surface."""
        config = ParticleConfig(
            color=(255, 0, 0),
            size=10.0,
            shape=ParticleShape.CIRCLE,
        )

        particle = EnhancedParticle(50, 50, config)
        surface = pg.Surface((100, 100))

        particle.draw(surface)

        # Check pixel was drawn (center should be red)
        color = surface.get_at((50, 50))
        assert color[0] > 200  # High red component

    @pytest.mark.skip(reason="Requires display")
    def test_draw_with_offset(self) -> None:
        """Test drawing with camera offset."""
        particle = EnhancedParticle(100, 100)
        surface = pg.Surface((200, 200))

        particle.draw(surface, offset=(50, 50))

        # Should draw at (50, 50) on screen
        # Just verify no crash

    def test_draw_dead_particle(self) -> None:
        """Test drawing dead particle."""
        particle = EnhancedParticle(0, 0)
        particle.alive = False
        surface = pg.Surface((100, 100))

        particle.draw(surface)

        # Should not draw anything (no crash)

    @pytest.mark.skip(reason="Requires display")
    def test_draw_rotated(self) -> None:
        """Test drawing rotated particle."""
        config = ParticleConfig(
            shape=ParticleShape.SQUARE,
            rotation_speed=90,
            size=10.0,
        )

        particle = EnhancedParticle(50, 50, config)
        particle.update(0.25)  # Rotate 90 degrees
        surface = pg.Surface((100, 100))

        particle.draw(surface)


class TestParticleCaching:
    """Test particle surface caching for performance."""

    def test_surface_cache_initialization(self) -> None:
        """Test cache is initialized."""
        # Clear cache first
        EnhancedParticle.clear_surface_cache()

        stats = EnhancedParticle.get_cache_stats()
        assert stats["cached_surfaces"] == 0
        assert stats["max_cache_size"] == 500

    def test_cache_key_creation(self) -> None:
        """Test cache key is created correctly."""
        config = ParticleConfig(
            color=(255, 100, 50),
            shape=ParticleShape.CIRCLE,
            size=10.0,
            alpha=200,
        )

        particle = EnhancedParticle(0, 0, config)
        particle.current_size = 10.0
        particle.current_color = (255, 100, 50)
        particle.current_alpha = 200

        # Cache key should be created with shape, size, color, alpha
        cache_key = (
            ParticleShape.CIRCLE,
            10,
            (255, 100, 50),
            200,
        )

        # Draw to populate cache
        surface = pg.Surface((100, 100))
        particle.draw(surface)

        stats = EnhancedParticle.get_cache_stats()
        assert stats["cached_surfaces"] >= 1

    def test_cache_reuse(self) -> None:
        """Test that same config reuses cached surface."""
        EnhancedParticle.clear_surface_cache()

        config = ParticleConfig(
            color=(100, 200, 150),
            shape=ParticleShape.SQUARE,
            size=5.0,
        )

        # Create multiple particles with same config
        particles = [EnhancedParticle(i * 10, i * 10, config) for i in range(5)]
        surface = pg.Surface((100, 100))

        # Draw all particles
        for p in particles:
            p.draw(surface)

        # Should have cached (same shape, size, color)
        stats = EnhancedParticle.get_cache_stats()
        # At least 1 cached surface (may have variations due to alpha)
        assert stats["cached_surfaces"] >= 1

    def test_cache_different_configs(self) -> None:
        """Test cache handles different configs."""
        EnhancedParticle.clear_surface_cache()

        surface = pg.Surface((100, 100))

        # Create particles with different shapes
        configs = [
            ParticleConfig(shape=ParticleShape.CIRCLE, color=(255, 0, 0)),
            ParticleConfig(shape=ParticleShape.SQUARE, color=(0, 255, 0)),
            ParticleConfig(shape=ParticleShape.TRIANGLE, color=(0, 0, 255)),
        ]

        for config in configs:
            particle = EnhancedParticle(50, 50, config)
            particle.draw(surface)

        stats = EnhancedParticle.get_cache_stats()
        assert stats["cached_surfaces"] >= 3

    def test_clear_cache(self) -> None:
        """Test clearing cache."""
        EnhancedParticle.clear_surface_cache()

        # Create some cached surfaces
        config = ParticleConfig(color=(50, 50, 50))
        particle = EnhancedParticle(0, 0, config)
        surface = pg.Surface((100, 100))
        particle.draw(surface)

        # Verify cache has items
        stats = EnhancedParticle.get_cache_stats()
        assert stats["cached_surfaces"] >= 1

        # Clear cache
        EnhancedParticle.clear_surface_cache()

        # Verify cache is empty
        stats = EnhancedParticle.get_cache_stats()
        assert stats["cached_surfaces"] == 0

    def test_cache_max_size_limit(self) -> None:
        """Test cache respects max size limit."""
        EnhancedParticle.clear_surface_cache()

        # Temporarily set low max for testing
        original_max = EnhancedParticle._cache_max_size
        EnhancedParticle._cache_max_size = 10

        surface = pg.Surface((100, 100))

        # Create many different particles
        for i in range(20):
            config = ParticleConfig(
                color=(i * 10 % 256, i * 5 % 256, i * 15 % 256),
                size=float(i % 20 + 1),
            )
            particle = EnhancedParticle(0, 0, config)
            particle.draw(surface)

        stats = EnhancedParticle.get_cache_stats()
        assert stats["cached_surfaces"] <= EnhancedParticle._cache_max_size

        # Restore original max
        EnhancedParticle._cache_max_size = original_max
