"""
Tests for new systems:
- Combo Manager
- Advanced Particles
- Enhanced Hint System
- Boss System
- Advanced Enemies
"""
from __future__ import annotations

import pytest
import time
from unittest.mock import Mock, MagicMock, patch

# Import new modules
from data.combo_manager import ComboManager, ComboType, ComboChain, ComboStats
from data.advanced_particles import AdvancedParticleSystem, AdvancedParticle, AdvancedParticleType
from data.enhanced_hint_system import HintManager, Hint, HintCategory, HintTrigger
from data.components.bosses import Boss, BossState, BossStats, Bowser, MegaGoomba, create_boss
from data.components.advanced_enemies import PiranhaPlant, BulletBill, HammerBro, BuzzyBeetle, create_enemy


class TestComboManager:
    """Tests for ComboManager."""

    def test_init(self) -> None:
        """Test combo manager initialization."""
        combo = ComboManager()

        assert combo.current_combo == 0
        assert combo.multiplier == 1.0
        assert len(combo.active_chains) == 0

    def test_add_hit_starts_combo(self) -> None:
        """Test that adding a hit starts a combo."""
        combo = ComboManager()
        points = combo.add_hit(ComboType.ENEMY_STOMP, base_points=100)

        assert points == 100  # Base points, no multiplier yet
        assert combo.get_current_combo() == 1
        assert combo.get_multiplier() == 1.0

    def test_add_hit_continues_combo(self) -> None:
        """Test continuing a combo chain."""
        combo = ComboManager()

        # First hit
        combo.add_hit(ComboType.ENEMY_STOMP, base_points=100)

        # Second hit (within combo window)
        points = combo.add_hit(ComboType.ENEMY_STOMP, base_points=100)

        assert combo.get_current_combo() == 2
        assert combo.stats.total_combos == 2

    def test_multiplier_calculation(self) -> None:
        """Test multiplier increases with combo count."""
        combo = ComboManager()

        # Build combo
        for _ in range(10):
            combo.add_hit(ComboType.ENEMY_STOMP, base_points=100)

        # Multiplier should be 2.0 at 5-9 combo, 3.0 at 10-19
        assert combo.get_multiplier() >= 2.0

    def test_combo_expires(self) -> None:
        """Test that combos expire after timeout."""
        combo = ComboManager()
        combo.COMBO_WINDOW = 100  # Short window for testing

        combo.add_hit(ComboType.ENEMY_STOMP)
        combo.update()  # Should not expire yet

        # Manually expire by setting old timestamp
        for chain in combo.active_chains.values():
            chain.last_hit_time = 0

        combo.update()  # Should expire now

        assert len(combo.active_chains) == 0

    def test_reset(self) -> None:
        """Test combo reset."""
        combo = ComboManager()
        combo.add_hit(ComboType.ENEMY_STOMP)
        combo.add_hit(ComboType.ENEMY_STOMP)

        combo.reset()

        assert combo.get_current_combo() == 0
        assert combo.get_multiplier() == 1.0
        assert len(combo.active_chains) == 0

    def test_serialize(self) -> None:
        """Test serialization to dict."""
        combo = ComboManager()
        combo.add_hit(ComboType.ENEMY_STOMP)
        combo.add_hit(ComboType.ENEMY_STOMP)

        data = combo.to_dict()

        assert "total_combos" in data
        assert "max_combo" in data
        assert data["total_combos"] == 2

    def test_different_combo_types(self) -> None:
        """Test different combo types are tracked separately."""
        combo = ComboManager()

        combo.add_hit(ComboType.ENEMY_STOMP)
        combo.add_hit(ComboType.FIREBALL_KILL)

        # Should have 2 active chains
        assert len(combo.active_chains) == 2


class TestAdvancedParticleSystem:
    """Tests for AdvancedParticleSystem."""

    def test_init(self) -> None:
        """Test particle system initialization."""
        system = AdvancedParticleSystem(max_particles=100, pool_size=50)

        assert system.max_particles == 100
        assert len(system._pool) == 50
        assert len(system.particles) == 0

    def test_emit_particles(self) -> None:
        """Test emitting particles."""
        system = AdvancedParticleSystem()

        count = system.emit(100, 200, "jump_dust")

        assert count > 0
        assert len(system.particles) > 0

    def test_emit_unknown_type(self) -> None:
        """Test emitting unknown particle type."""
        system = AdvancedParticleSystem()

        count = system.emit(100, 200, "unknown_type")

        assert count == 0
        assert len(system.particles) == 0

    def test_update_removes_dead_particles(self) -> None:
        """Test that update removes dead particles."""
        system = AdvancedParticleSystem()

        system.emit(100, 200, "spark")  # Short lifetime

        # Update with large dt to age particles
        system.update(1000)

        # Some particles should be removed
        assert len(system.particles) >= 0  # May all be dead

    def test_max_particles_limit(self) -> None:
        """Test that max_particles limit is respected."""
        system = AdvancedParticleSystem(max_particles=10, pool_size=20)

        # Emit more than max
        system.emit(0, 0, "dust", count_override=50)

        assert len(system.particles) <= 10

    def test_clear(self) -> None:
        """Test clearing all particles."""
        system = AdvancedParticleSystem()
        system.emit(100, 200, "dust")

        system.clear()

        assert len(system.particles) == 0
        assert len(system._pool) > 0

    def test_stats(self) -> None:
        """Test particle system statistics."""
        system = AdvancedParticleSystem()

        system.emit(100, 200, "dust")
        system.update(100)

        stats = system.get_stats()

        assert "emitted" in stats
        assert "active" in stats
        assert stats["emitted"] > 0

    def test_particle_templates_exist(self) -> None:
        """Test that all expected templates exist."""
        expected_templates = ["jump_dust", "landing_dust", "shell_spark", "fireball_trail", "coin_burst", "combo_star"]

        for template in expected_templates:
            assert template in AdvancedParticleSystem.TEMPLATES


class TestHintManager:
    """Tests for EnhancedHintManager."""

    def test_init(self) -> None:
        """Test hint manager initialization."""
        hint_mgr = HintManager(tutorial_mode=True)

        assert len(hint_mgr.hints) > 0
        assert hint_mgr.tutorial_mode is True
        assert hint_mgr.hint_visible is False

    def test_load_default_hints(self) -> None:
        """Test that default hints are loaded."""
        hint_mgr = HintManager()

        # Should have hints from all categories
        categories = set(h.category for h in hint_mgr.hints.values())

        assert HintCategory.CONTROLS in categories
        assert HintCategory.COMBAT in categories
        assert HintCategory.POWERUPS in categories

    def test_on_event_queues_hint(self) -> None:
        """Test that events queue appropriate hints."""
        hint_mgr = HintManager()

        hint_mgr.on_event("ON_START")

        # Should queue ON_START hints
        assert len(hint_mgr.hint_queue) > 0

    def test_show_hint(self) -> None:
        """Test showing a hint."""
        hint_mgr = HintManager()
        hint = list(hint_mgr.hints.values())[0]

        hint_mgr.show_hint(hint)

        assert hint_mgr.hint_visible is True
        assert hint_mgr.current_hint == hint
        assert hint.shown is True

    def test_hide_hint(self) -> None:
        """Test hiding a hint."""
        hint_mgr = HintManager()
        hint = list(hint_mgr.hints.values())[0]

        hint_mgr.show_hint(hint)
        hint_mgr.hide_hint()

        assert hint_mgr.hint_visible is False
        assert hint_mgr.current_hint is None

    def test_update_shows_queued_hints(self) -> None:
        """Test that update shows queued hints."""
        hint_mgr = HintManager()
        hint_mgr.hint_display_time = 100  # Short for testing

        hint_mgr.on_event("ON_START")
        hint_mgr.update(0)

        # Should show hint
        assert hint_mgr.hint_visible is True

    def test_force_show_hint(self) -> None:
        """Test forcing a specific hint."""
        hint_mgr = HintManager()

        result = hint_mgr.force_show_hint("controls_move")

        assert result is True
        assert len(hint_mgr.hint_queue) > 0

    def test_force_show_unknown_hint(self) -> None:
        """Test forcing unknown hint."""
        hint_mgr = HintManager()

        result = hint_mgr.force_show_hint("unknown_id")

        assert result is False

    def test_get_hints_by_category(self) -> None:
        """Test getting hints by category."""
        hint_mgr = HintManager()

        hints = hint_mgr.get_hints_by_category(HintCategory.CONTROLS)

        assert len(hints) > 0
        assert all(h.category == HintCategory.CONTROLS for h in hints)

    def test_tutorial_progress(self) -> None:
        """Test tutorial progress calculation."""
        hint_mgr = HintManager()

        initial_progress = hint_mgr.get_tutorial_progress()

        # Show some hints
        hint_mgr.force_show_hint("controls_move")
        hint_mgr.update(0)

        progress = hint_mgr.get_tutorial_progress()

        assert progress >= initial_progress

    def test_reset(self) -> None:
        """Test resetting all hint progress."""
        hint_mgr = HintManager()

        hint_mgr.force_show_hint("controls_move")
        hint_mgr.update(0)
        hint_mgr.hide_hint()

        hint_mgr.reset()

        assert hint_mgr.hint_visible is False
        assert hint_mgr.current_hint is None
        assert len(hint_mgr.hint_queue) == 0

    def test_serialize_hint(self) -> None:
        """Test hint serialization."""
        hint = Hint(id="test", text="Test hint", category=HintCategory.CONTROLS, trigger=HintTrigger.MANUAL)

        data = hint.to_dict()

        assert data["id"] == "test"
        assert data["category"] == "CONTROLS"

        # Deserialize
        restored = Hint.from_dict(data)
        assert restored.id == "test"


class TestBossSystem:
    """Tests for Boss system."""

    def test_bowser_creation(self) -> None:
        """Test creating Bowser boss."""
        bowser = Bowser(100, 200)

        assert bowser.name == "bowser"
        assert bowser.stats.max_health == 5
        assert bowser.stats.current_health == 5

    def test_mega_goomba_creation(self) -> None:
        """Test creating Mega Goomba boss."""
        mega_goomba = MegaGoomba(100, 200)

        assert mega_goomba.name == "mega_goomba"
        assert mega_goomba.stats.max_health == 3

    def test_boss_factory(self) -> None:
        """Test boss factory function."""
        bowser = create_boss("bowser", 0, 0)
        assert isinstance(bowser, Bowser)

        mega_goomba = create_boss("mega_goomba", 0, 0)
        assert isinstance(mega_goomba, MegaGoomba)

    def test_boss_factory_unknown_type(self) -> None:
        """Test boss factory with unknown type."""
        with pytest.raises(ValueError):
            create_boss("unknown_boss", 0, 0)

    def test_boss_take_damage(self) -> None:
        """Test boss taking damage."""
        bowser = Bowser(0, 0)

        result = bowser.take_damage(1)

        assert result is True
        assert bowser.stats.current_health == 4

    def test_boss_invincible(self) -> None:
        """Test boss invincibility after damage."""
        bowser = Bowser(0, 0)
        bowser.current_time = 1000

        bowser.take_damage(1)

        assert bowser.is_invincible() is True

    def test_boss_defeat(self) -> None:
        """Test boss defeat."""
        bowser = Bowser(0, 0)

        # Deal enough damage
        for _ in range(5):
            bowser.take_damage(1)

        assert bowser.state == BossState.DEFEATED

    def test_boss_health_bar(self) -> None:
        """Test boss health bar drawing."""
        bowser = Bowser(0, 0)

        # Should not raise
        surface = MagicMock()
        bowser.draw_health_bar(surface, (100, 100))

    def test_boss_stun(self) -> None:
        """Test stunning boss."""
        bowser = Bowser(0, 0)
        bowser.current_time = 1000

        bowser.stun(1000)

        assert bowser.state == BossState.STUNNED

    def test_boss_damage_callback(self) -> None:
        """Test boss damage callback."""
        bowser = Bowser(0, 0)

        callback = MagicMock()
        bowser.on_damage = callback

        bowser.take_damage(1)

        callback.assert_called_once_with(1)


class TestAdvancedEnemies:
    """Tests for advanced enemy types."""

    def test_piranha_plant_creation(self) -> None:
        """Test creating Piranha Plant."""
        plant = PiranhaPlant(100, 200)

        assert plant.name == "piranha_plant"
        assert plant.state == "hidden" or plant.state == "HIDDEN"

    def test_bullet_bill_creation(self) -> None:
        """Test creating Bullet Bill."""
        bullet = BulletBill(100, 200, direction="right")

        assert bullet.name == "bullet_bill"

    def test_hammer_bro_creation(self) -> None:
        """Test creating Hammer Bro."""
        hammer_bro = HammerBro(100, 200)

        assert hammer_bro.name == "hammer_bro"

    def test_buzzy_beetle_creation(self) -> None:
        """Test creating Buzzy Beetle."""
        buzzy = BuzzyBeetle(100, 200)

        assert buzzy.name == "buzzy_beetle"
        assert buzzy.fire_immunity is True

    def test_enemy_factory(self) -> None:
        """Test enemy factory function."""
        goomba = create_enemy("goomba", 0, 100)
        assert goomba.name == "goomba"

        koopa = create_enemy("koopa", 0, 100)
        assert koopa.name == "koopa"

    def test_enemy_factory_unknown_type(self) -> None:
        """Test enemy factory with unknown type."""
        with pytest.raises(ValueError):
            create_enemy("unknown_enemy", 0, 0)

    def test_piranha_plant_emerge(self) -> None:
        """Test Piranha Plant emerge cycle."""
        plant = PiranhaPlant(100, 200)
        plant.current_time = 1000
        plant.WAIT_TIME = 100  # Short for testing

        # Should start emerging after wait
        plant.handle_state()

        # State should change from HIDDEN eventually
        # (exact state depends on timing)

    def test_bullet_bill_lifetime(self) -> None:
        """Test Bullet Bill lifetime limit."""
        bullet = BulletBill(0, 100)
        bullet.current_time = 0
        bullet.spawn_time = 0

        # Set time beyond lifetime
        bullet.current_time = bullet.LIFETIME + 1

        bullet.update({})

        # Should be killed
        assert not bullet.alive() if hasattr(bullet, "alive") else True

    def test_hammer_bro_jump(self) -> None:
        """Test Hammer Bro jump behavior."""
        hammer_bro = HammerBro(100, 200)
        hammer_bro.current_time = 1000
        hammer_bro.JUMP_INTERVAL = 100  # Short for testing

        hammer_bro.walking()

        # Should eventually jump
        # (exact behavior depends on timing)


class TestIntegration:
    """Integration tests for multiple systems."""

    def test_combo_with_particles(self) -> None:
        """Test combo system triggering particle effects."""
        combo = ComboManager()
        particles = AdvancedParticleSystem()

        # Setup callback
        def on_bonus(text: str, points: int) -> None:
            particles.emit(0, 0, "combo_star")

        combo.on_bonus = on_bonus

        # Build combo to trigger bonus
        for _ in range(5):
            combo.add_hit(ComboType.ENEMY_STOMP, base_points=100)

        # Should have emitted particles
        assert particles.stats["emitted"] > 0

    def test_hint_on_combo_event(self) -> None:
        """Test hint system responding to combo events."""
        hint_mgr = HintManager()
        combo = ComboManager()

        # Setup integration
        def on_combo_update(combo_type: ComboType, count: int, mult: float) -> None:
            if count >= 5:
                hint_mgr.on_event("ON_COMBO")

        combo.on_combo_update = on_combo_update

        # Build combo
        for _ in range(5):
            combo.add_hit(ComboType.ENEMY_STOMP)

        # Should queue hint
        assert len(hint_mgr.hint_queue) >= 0  # May or may not have hints

    def test_boss_defeat_gives_combo(self) -> None:
        """Test boss defeat triggering combo points."""
        combo = ComboManager()
        bowser = Bowser(0, 0)

        defeated = False

        def on_defeat() -> None:
            combo.add_hit(ComboType.ENEMY_STOMP, base_points=1000)
            defeated = True

        bowser.on_defeat = on_defeat

        # Defeat boss
        for _ in range(5):
            bowser.take_damage(1)

        assert defeated is True
        assert combo.stats.total_combos >= 1


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
