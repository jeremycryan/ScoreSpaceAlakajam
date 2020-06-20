import pygame
import constants as c
from corridor import Corridor
from player import Player
from enemy import Dasher, Crawler, CrawlerCeiling
import random


class Scene:
    def __init__(self, game):
        self.game = game

    def main(self):
        pass

    def next_scene(self):
        raise NotImplementedError("Scene must implement next_scene")


class ConnectionScene(Scene):

    def main(self):
        clock = pygame.time.Clock()
        self.corridor = self.game.corridor
        self.corridor.x = 0
        self.player = self.game.player
        self.game.enemies = []
        self.game.pickups = []
        self.since_enemy = 0
        self.game.scroll_speed = 0
        self.spawn_dasher()

        while True:
            dt = clock.tick(60)/1000
            events = self.game.update_globals()

            self.corridor.update(dt, events)
            self.player.update(dt, events)
            self.game.update_screenshake(dt, events)
            self.update_scrolling(dt, events)
            self.update_enemies(dt, events)
            self.update_pickups(dt, events)
            self.update_particles(dt, events)

            self.game.screen.fill((120, 120, 120))
            self.corridor.draw(self.game.screen)
            for particle in self.game.particles:
                particle.draw(self.game.screen)
            for enemy in self.game.enemies:
                enemy.draw(self.game.screen)
            for pickup in self.game.pickups:
                pickup.draw(self.game.screen)
            self.player.draw(self.game.screen)
            pygame.display.flip()

    def update_scrolling(self, dt, events):
        if self.game.scroll_speed < 350:
            self.game.scroll_speed += 200 * dt
            if self.game.scroll_speed >= 350:
                self.game.scroll_speed = 350

    def update_pickups(self, dt, events):
        for item in self.game.pickups[::-1]:
            item.update(dt, events)
            if c.distance_between_points(item.x, item.y, self.player.x, self.player.y) < self.player.width//2:
                item.get()
                self.game.pickups.remove(item)

    def update_particles(self, dt, events):
        for particle in self.game.particles[::-1]:
            particle.update(dt, events)
            if particle.dead:
                self.game.particles.remove(particle)

    def update_enemies(self, dt, events):
        for enemy in self.game.enemies:
            enemy.update(dt, events)
        self.since_enemy += dt
        if self.since_enemy > 1:
            choices = [self.spawn_crawler_wave,
                    self.spawn_crawler_ceiling_wave,
                    self.spawn_dasher]
            random.choice(choices)()
            self.since_enemy = 0
        for enemy in self.game.enemies[::-1]:
            if enemy.dead and enemy.remove_on_death:
                self.game.enemies.remove(enemy)
            elif enemy.x < -500 or enemy.x > c.WINDOW_WIDTH + 500 or enemy.y < -500 or enemy.y > c.WINDOW_HEIGHT + 500:
                self.game.enemies.remove(enemy)

    def spawn_dasher(self):
        new_enemy = Dasher(self.game, 0, 0)
        y_min = c.WINDOW_HEIGHT//2 - self.corridor.width//2 + new_enemy.radius
        y_max = y_min + self.corridor.width - new_enemy.radius*2
        y = random.random() * (y_max - y_min) + y_min
        x = c.WINDOW_WIDTH + new_enemy.radius
        new_enemy.y = y
        new_enemy.x = x
        self.game.enemies.append(new_enemy)

    def spawn_crawler_wave(self, length=3):
        spacing = 72
        for i in range(length):
            new_enemy = Crawler(self.game, c.WINDOW_WIDTH + 50 + spacing*i, 0)
            self.game.enemies.append(new_enemy)

    def spawn_crawler_ceiling_wave(self, length=3):
        spacing = 72
        for i in range(length):
            new_enemy = CrawlerCeiling(self.game, c.WINDOW_WIDTH + 50 + spacing*i, 0)
            self.game.enemies.append(new_enemy)
