"""Level 5 state for Super Mario Bros - Castle/Fortress theme."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import pygame as pg

from .. import setup, tools
from .. import constants as c
from ..components import mario
from ..components import collider
from ..components import bricks
from ..components import coin_box
from ..components import enemies
from ..components import advanced_enemies
from ..components import checkpoint
from ..components import flagpole
from ..components import info
from ..components import score
from .. import level_loader

logger = logging.getLogger(__name__)


class Level5(tools._State):
    """Level 5 - Castle/Fortress themed level (final)"""

    def __init__(self) -> None:
        tools._State.__init__(self)
        self.level_file = "data/levels/level_5_1.json"

    def startup(self, current_time: float, persist: Dict[str, Any]) -> None:
        """Called when the State object is created"""
        self.game_info = persist
        self.persist = self.game_info
        self.game_info[c.CURRENT_TIME] = current_time
        self.game_info[c.LEVEL_STATE] = c.NOT_FROZEN
        self.game_info[c.MARIO_DEAD] = False

        self.state = c.NOT_FROZEN
        self.death_timer: float = 0
        self.flag_timer: float = 0
        self.flag_score: Optional[Any] = None

        self.moving_score_list: List[score.Score] = []
        self.overhead_info_display = info.OverheadInfo(self.game_info, c.LEVEL)

        self.background: Optional[pg.Surface] = None
        self.back_rect: Optional[pg.Rect] = None
        self.level: Optional[pg.Surface] = None
        self.level_rect: Optional[pg.Rect] = None
        self.viewport: Optional[pg.Rect] = None
        self.ground_group: Optional[pg.sprite.Group] = None
        self.pipe_group: Optional[pg.sprite.Group] = None
        self.step_group: Optional[pg.sprite.Group] = None
        self.brick_group: Optional[pg.sprite.Group] = None
        self.coin_box_group: Optional[pg.sprite.Group] = None
        self.flag_pole_group: Optional[pg.sprite.Group] = None
        self.enemy_group: Optional[pg.sprite.Group] = None
        self.mario: Optional[mario.Mario] = None
        self.checkpoint_group: Optional[pg.sprite.Group] = None
        self.flag: Optional[flagpole.Flag] = None
        self.pole: Optional[flagpole.Pole] = None
        self.finial: Optional[flagpole.Finial] = None
        self.coin_group: Optional[pg.sprite.Group] = None
        self.powerup_group: Optional[pg.sprite.Group] = None
        self.fire_group: Optional[pg.sprite.Group] = None

        try:
            self.level_data = level_loader.load_level_from_json(self.level_file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load level: {e}")
            self.next = c.GAME_OVER
            self.done = True
            return
        self._init_groups()
        self.setup_all()

    def _init_groups(self) -> None:
        """Initialize sprite groups early"""
        self.ground_group = pg.sprite.Group()
        self.pipe_group = pg.sprite.Group()
        self.step_group = pg.sprite.Group()
        self.brick_group = pg.sprite.Group()
        self.coin_box_group = pg.sprite.Group()
        self.flag_pole_group = pg.sprite.Group()
        self.enemy_group = pg.sprite.Group()
        self.checkpoint_group = pg.sprite.Group()
        self.coin_group = pg.sprite.Group()
        self.powerup_group = pg.sprite.Group()
        self.fire_group = pg.sprite.Group()

    def setup_all(self) -> None:
        """Setup all level components"""
        self.setup_background()
        self.setup_ground()
        self.setup_pipes()
        self.setup_steps()
        self.setup_bricks()
        self.setup_coin_boxes()
        self.setup_flag_pole()
        self.setup_enemies()
        self.setup_mario()
        self.setup_checkpoints()

    def setup_background(self) -> None:
        """Sets the background"""
        self.background = setup.GFX.get("level_1", pg.Surface((self.level_data.width, self.level_data.height)))
        self.background.fill(self.level_data.background_color)
        self.back_rect = self.background.get_rect()
        width = self.back_rect.width
        height = self.back_rect.height

        self.level = pg.Surface((width, height)).convert()
        self.level_rect = self.level.get_rect()
        self.viewport = setup.SCREEN.get_rect(bottom=self.level_rect.bottom)
        self.viewport.x = self.game_info.get(c.CAMERA_START_X, 0)

    def setup_ground(self) -> None:
        """Creates ground collision rectangles"""
        for section in getattr(self.level_data, "ground_sections", []):
            ground_rect = collider.Collider(section["x"], section["y"], section["width"], section["height"])
            self.ground_group.add(ground_rect)

    def setup_pipes(self) -> None:
        """Create pipe obstacles"""
        for p in getattr(self.level_data, "pipes", []):
            self.pipe_group.add(collider.Collider(p["x"], p["y"], p["width"], p["height"]))

    def setup_steps(self) -> None:
        """Create step obstacles"""
        for s in getattr(self.level_data, "steps", []):
            self.step_group.add(collider.Collider(s["x"], s["y"], s["width"], s["height"]))

    def setup_bricks(self) -> None:
        """Creates breakable bricks"""
        self.brick_pieces_group = pg.sprite.Group()
        for brick_info in getattr(self.level_data, "bricks", []):
            brick = bricks.Brick(brick_info["x"], brick_info["y"], contents=brick_info.get("contents"))
            self.brick_group.add(brick)

    def setup_coin_boxes(self) -> None:
        """Creates coin boxes"""
        for box_info in getattr(self.level_data, "coin_boxes", []):
            self.coin_box_group.add(coin_box.CoinBox(box_info["x"], box_info["y"], contents=box_info.get("contents")))

    def setup_flag_pole(self) -> None:
        """Creates flag pole"""
        flag_pole_data = getattr(self.level_data, "flag_pole", {})
        if flag_pole_data:
            self.flag = flagpole.Flag(flag_pole_data["x"], flag_pole_data["y"])
            self.pole = flagpole.Pole(flag_pole_data["x"], flag_pole_data["y"])
            self.finial = flagpole.Finial(flag_pole_data["x"], flag_pole_data["y"])
            self.flag_pole_group.add(self.flag, self.pole, self.finial)

    def setup_enemies(self) -> None:
        """Setup enemies"""
        enemy_map = {
            "goomba": enemies.Goomba,
            "koopa": enemies.Koopa,
            "piranha": advanced_enemies.PiranhaPlant,
            "bullet_bill": advanced_enemies.BulletBill,
            "hammer_bro": advanced_enemies.HammerBro,
        }
        for enemy_info in getattr(self.level_data, "enemies", []):
            enemy_type = enemy_info.get("type", "goomba")
            enemy_class = enemy_map.get(enemy_type)
            if enemy_class is None:
                logger.warning(f"Unknown enemy type: {enemy_type}, using Goomba")
                enemy_class = enemies.Goomba
            x = enemy_info.get("x", 0)
            y = enemy_info.get("y", c.GROUND_HEIGHT)
            direction = enemy_info.get("direction", "left")
            self.enemy_group.add(enemy_class(x, y, direction))

    def setup_mario(self) -> None:
        """Setup Mario"""
        mario_start = getattr(self.level_data, "mario_start", {"x": 110, "y": c.GROUND_HEIGHT})
        self.mario = mario.Mario()
        if self.mario:
            self.mario.rect.x = mario_start.get("x", 110)
            self.mario.rect.y = mario_start.get("y", c.GROUND_HEIGHT)

    def setup_checkpoints(self) -> None:
        """Setup checkpoints"""
        for cp_info in getattr(self.level_data, "checkpoints", []):
            self.checkpoint_group.add(
                checkpoint.Checkpoint(
                    cp_info["x"],
                    cp_info.get("y", 0),
                    cp_info.get("width", 10),
                    cp_info.get("height", 600),
                    cp_info["name"],
                )
            )

    def update(self, surface: pg.Surface, keys: tuple, current_time: float) -> None:
        """Update level state"""
        self.current_time = current_time

        if self.state == c.FROZEN:
            self.draw(surface)
            return

        if self.state == c.NOT_FROZEN:
            self.moving_score_list = self.overhead_info_display.moving_score_list if self.overhead_info_display else []

            if self.game_info.get(c.MARIO_DEAD):
                self.death_timer += 1
                if self.death_timer == 90 and self.mario:
                    self.mario.update((), self.current_time)
                elif self.death_timer == 120:
                    self.next = c.GAME_OVER
                    self.done = True
            elif self.game_info.get(c.FLAG_AND_FIREWORKS):
                self.flag_timer = current_time - (self.flag_score.start_time if self.flag_score else current_time)
                if self.flag_timer >= 200:
                    self.game_info["current_level"] = c.LEVEL5
                    self.next = c.GAME_OVER
                    self.done = True
            else:
                self.update_entities(keys, current_time)
                self.check_collisions()
                self.check_checkpoints()
                self.check_state_triggers()
                if self.mario and not self.mario.dead:
                    self.update_viewport()

        self.draw(surface)

    def update_entities(self, keys: tuple, current_time: float) -> None:
        """Update all entities"""
        if self.mario:
            self.mario.update(keys, current_time)
        if self.enemy_group:
            self.enemy_group.update(current_time)
        if self.powerup_group:
            self.powerup_group.update(current_time)
        if self.fire_group:
            self.fire_group.update(current_time)
        if self.brick_group:
            self.brick_group.update()
        if self.coin_box_group:
            self.coin_box_group.update()

    def check_collisions(self) -> None:
        """Check collisions"""
        if not self.mario:
            return

        for group in [
            self.ground_group,
            self.pipe_group,
            self.step_group,
            self.brick_group,
            self.coin_box_group,
            self.enemy_group,
        ]:
            collide = pg.sprite.spritecollideany(self.mario, group)
            if collide:
                self.mario.adjust_for_collisions(collide)

        if self.powerup_group:
            powerup = pg.sprite.spritecollideany(self.mario, self.powerup_group)
            if powerup:
                powerup.collide_action(self.mario, self.game_info, self.current_time)

        if self.coin_group:
            coin = pg.sprite.spritecollideany(self.mario, self.coin_group)
            if coin:
                coin.kill()
                self.game_info[c.SCORE] += 200
                self.game_info[c.COIN_TOTAL] += 1

    def check_checkpoints(self) -> None:
        """Check checkpoints"""
        if self.mario and self.checkpoint_group:
            checkpoint = pg.sprite.spritecollideany(self.mario, self.checkpoint_group)
            if checkpoint:
                checkpoint.kill()

    def check_state_triggers(self) -> None:
        """Check state triggers"""
        if self.mario and self.mario.dead:
            self.state = c.FROZEN
            self.game_info[c.MARIO_DEAD] = True

        if self.mario and self.flag_pole_group:
            flag_pole = pg.sprite.spritecollideany(self.mario, self.flag_pole_group)
            if flag_pole and hasattr(flag_pole, "state") and flag_pole.state == c.TOP_OF_POLE:
                self.state = c.FLAG_AND_FIREWORKS
                self.flag_score = score.Score(self.mario.rect.centerx, self.mario.rect.y, c.SCORE_FLAG_POLE_TOP)
                self.moving_score_list.append(self.flag_score)

    def update_viewport(self) -> None:
        """Update viewport"""
        if not self.mario or not self.viewport:
            return

        level_rect = self.level_rect
        if self.mario.rect.right > self.viewport.centerx:
            self.viewport.centerx = self.mario.rect.centerx
            self.viewport.right = min(self.viewport.right, level_rect.right)

        if self.mario.rect.left < self.viewport.x:
            self.mario.rect.left = self.viewport.x

        self.viewport.x = max(0, self.viewport.x)
        self.viewport.right = min(self.viewport.right, level_rect.right)

    def draw(self, surface: pg.Surface) -> None:
        """Render level"""
        if self.level is None or self.background is None:
            return

        self.level.blit(self.background, self.back_rect, self.viewport)

        for group in [
            self.ground_group,
            self.pipe_group,
            self.step_group,
            self.brick_group,
            self.coin_box_group,
            self.flag_pole_group,
            self.enemy_group,
            self.powerup_group,
            self.coin_group,
            self.fire_group,
        ]:
            if group:
                group.draw(self.level)

        if self.mario:
            self.mario.draw(self.level)
        if self.overhead_info_display:
            self.overhead_info_display.draw(self.level)

        surface.blit(self.level, (0, 0), self.viewport)

    def get_event(self, event: pg.event.Event) -> None:
        """Handle events"""
        if self.mario:
            self.mario.get_event(event)
