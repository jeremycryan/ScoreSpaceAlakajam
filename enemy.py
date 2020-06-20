import pygame
import constants as c
import random
import math


class Enemy:
    def __init__(self, game, x, y, radius=60):
        self.game = game
        self.radius = radius
        self.x = x
        self.y = y
        self.age = 0
        self.dead = False
        self.hp = 3

    def die(self):
        self.dead = True

    def update(self, dt, events):
        self.age += dt
        self.check_player_bullets()
        if self.hp <= 0:
            self.die()

    def draw(self, surface):
        pass

    def check_player_bullets(self):
        to_destroy = set()
        for item in self.game.player.bullets:
            if c.distance_between_points(item.x, item.y, self.x, self.y) < item.radius + self.radius:
                self.get_hit_by(item)
                to_destroy.add(item)
        self.game.player.bullets -= to_destroy

    def get_hit_by(self, bullet):
        self.hp -= 1

    def is_colliding_with_player(self, player):
        # test center of circle inside player
        if self.x < player.x + player.width//2:
            if self.x > player.x - player.width//2:
                if self.y < player.y + player.height//2:
                    if self.y > player.y - player.height//2:
                        return True

        # test collision in cardinal directions
        if self.x < player.x + player.width//2 and self.x > player.x - player.width//2:
            # top
            if self.y < player.y:
                if self.y > player.y - player.height//2 - self.radius:
                    return True
            # bottom
            if self.y > player.y:
                if self.y < player.y + player.height//2 + self.radius:
                    return True
        if self.y < player.y + player.height//2 and self.y > player.y - player.height//2:
            # left
            if self.x < player.x:
                if self.x > player.x - player.width//2 - self.radius:
                    return True
            # right
            if self.x > player.x:
                if self.x < player.x + player.width//2 + self.radius:
                    return True

        # test collisions with corners
        c1 = player.x - player.width//2, player.y - player.height//2
        c2 = player.x + player.width//2, player.y - player.height//2
        c3 = player.x - player.width//2, player.y + player.height//2
        c4 = player.x + player.width//2, player.y + player.height//2
        corners = (c1, c2, c3, c4)
        for item in corners:
            if c.distance_between_points(self.x, self.y, *item) < self.radius:
                return True

        return False


class Dasher(Enemy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hover_x = c.WINDOW_WIDTH * 0.8

        self.hover_length = 2
        self.x_velocity = 0
        self.hp = 7

        self.shiver_x = 0
        self.shiver_y = 0
        self.shiver_target = [1, 0]
        self.shiver_intensity = 0

    def update(self, dt, events):
        super().update(dt, events)

        if abs(self.shiver_x - self.shiver_target[0]) < 10 and abs(self.shiver_y - self.shiver_target[1]) < 10:
            self.shiver_target[0] = random.random() * 2 * self.shiver_intensity - self.shiver_intensity
            self.shiver_target[1] = random.random() * 2 * self.shiver_intensity - self.shiver_intensity

        if self.age < self.hover_length:
            if self.x > self.hover_x:
                self.x -= (self.x - self.hover_x) * 7 * dt
            self.shiver_intensity = self.age * 10
        else:
            self.x_velocity = -1600
            self.x += self.x_velocity * dt
            self.shiver_target = [0, 0]

        self.shiver_x += (self.shiver_target[0] - self.shiver_x) * self.shiver_intensity * dt * 2
        self.shiver_y += (self.shiver_target[1] - self.shiver_y) * self.shiver_intensity * dt * 2

        self.check_player_bullets()
        if self.hp <= 0:
            self.die()

    def draw(self, surface):
        if not self.is_colliding_with_player(self.game.player):
            color = c.RED
        else:
            color = c.BLUE
        x, y = int(self.x + self.shiver_x), int(self.y + self.shiver_y)
        pygame.draw.circle(surface, color, (x, y), self.radius)


class Crawler(Enemy):
    CRAWLING = 0
    LAUNCHING = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.speed = -400
        self.velocity = [0, 0]
        self.launch_speed = 1000
        self.state = self.CRAWLING
        self.radius = 24
        self.y = c.WINDOW_HEIGHT//2 + self.game.corridor.width//2 - self.radius
        self.hp = 2

        self.detect_range = 200

    def update(self, dt, events):
        super().update(dt, events)

        dx = self.x - self.game.player.x
        if dx < self.detect_range and self.state == self.CRAWLING:
            self.state = self.LAUNCHING
            self.velocity = self.launch_velocity()

        if self.state == self.CRAWLING:
            self.x += self.speed * dt
        elif self.state == self.LAUNCHING:
            self.velocity[1] += 2000*dt
            self.x += self.velocity[0] * dt
            self.y += self.velocity[1] * dt

    def launch_velocity(self):
        angle = math.pi * 3/4
        angle += (random.random() * math.pi/6) - math.pi/12
        x = math.cos(angle) * self.launch_speed
        y = -math.sin(angle) * self.launch_speed
        return [x, y]

    def draw(self, surface):
        if not self.is_colliding_with_player(self.game.player):
            color = c.RED
        else:
            color = c.BLUE
        x, y = int(self.x), int(self.y)
        pygame.draw.circle(surface, color, (x, y), self.radius)


class CrawlerCeiling(Crawler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.y = c.WINDOW_HEIGHT//2 - self.game.corridor.width//2 + self.radius
        self.launch_speed = 500

    def launch_velocity(self):
        angle = math.pi * 1.25
        angle += (random.random() * math.pi/4) - math.pi/8
        x = math.cos(angle) * self.launch_speed
        y = -math.sin(angle) * self.launch_speed
        return [x, y]
