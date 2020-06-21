import pygame
import constants as c
from sprite_tools import SpriteSheet, Sprite
import random


cash1 = SpriteSheet("images/cash1.png", (6, 1), 6, scale=2)
cash2 = SpriteSheet("images/cash2.png", (6, 1), 6, scale=2)
cash3 = SpriteSheet("images/cash3.png", (6, 1), 6, scale=2)


class Pickup:
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y

    def update(self, dt, events):
        pass

    def draw(self, surface):
        pass

class Cash(Pickup):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.sprite = Sprite(10)
        self.sprite.add_animation({"Idle": random.choice([cash1, cash2, cash3])})
        self.sprite.start_animation("Idle")
        self.sprite.now += random.random()

        xv = random.random()**2 * 1300
        yv = random.random()**2 * -300 - 100
        self.velocity = [xv, yv]

        self.homing_range = 120
        self.terminal_velocity = random.random() * 120 + 50

        self.paused = False

    def update(self, dt, events):
        if not self.paused:
            self.sprite.update(dt)
        if self.game.scroll_speed < 50:
            self.homing_range = 400

        self.velocity[0] *= 0.05 **dt
        self.velocity[1] += 1000 * dt
        self.velocity[1] = min(self.terminal_velocity, self.velocity[1])

        if c.distance_between_points(self.x, self.y, self.game.player.x, self.game.player.y) < self.homing_range and self.x >= -150:
            dx = self.game.player.x - self.x
            dy = self.game.player.y - self.y
            self.velocity[0] = dx * 12 + self.game.scroll_speed
            self.velocity[1] = dy * 12

        self.x += (self.velocity[0] - self.game.scroll_speed) * dt
        if self.y < self.game.corridor.floor_y() or self.velocity[1] < 0:
            self.y += self.velocity[1] * dt

        if self.y >= self.game.corridor.floor_y() - 10:
            self.paused = True

    def draw(self, surface):
        sx, sy = self.game.get_shake_offset()
        x, y = int(self.x + sx), int(self.y + sy)
        self.sprite.set_position((x, y))
        self.sprite.draw(surface)

    def get(self):
        self.game.player.cash_this_level += 5
        self.game.pickup_sound.play()
