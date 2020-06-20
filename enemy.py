import pygame
import constants as c
import random
import math
from sprite_tools import SpriteSheet, Sprite
from pickup import Cash
from particle import DasherSmoke, DasherSmokeRed


crawler_running = SpriteSheet("images/crawler.png", (4, 1), 4, scale=2)
crawler_running_ceiling = SpriteSheet("images/crawler.png", (4, 1), 4, scale=2)
crawler_running_ceiling.reverse(0, 1)
crawler_jump = SpriteSheet("images/crawler_jump.png", (1, 1), 1, scale=2)
crawler_hurt = SpriteSheet("images/crawler_hurt.png", (1, 1), 1, scale=2)
crawler_hurt_ceiling = SpriteSheet("images/crawler_hurt.png", (1, 1), 1, scale=2)
crawler_hurt_ceiling.reverse(0, 1)
crawler_dead = SpriteSheet("images/crawler_dead.png", (1, 1), 1, scale=2)

dasher_hovering = SpriteSheet("images/dasher.png", (1, 1), 1, scale=2)
dasher_dashing = SpriteSheet("images/dasher_dashing.png", (1, 1), 1, scale=2)
dasher_damage = SpriteSheet("images/dasher_damage.png", (1, 1), 1, scale=2)
dasher_dashing_damage = SpriteSheet("images/dasher_dashing_damage.png", (1, 1), 1, scale=2)


class Enemy:
    def __init__(self, game, x, y, radius=60):
        self.game = game
        self.radius = radius
        self.x = x
        self.y = y
        self.age = 0
        self.dead = False
        self.hp = 3
        self.value = 1
        self.remove_on_death = True

    def die(self):
        self.dead = True
        for i in range(self.value):
            self.game.pickups.append(Cash(self.game, self.x, self.y))

    def update(self, dt, events):
        self.age += dt
        self.check_player_bullets()
        if self.is_colliding_with_player(self.game.player):
            self.game.player.get_hit_by(self)

    def draw(self, surface):
        pass

    def check_player_bullets(self):
        if self.dead:
            return
        to_destroy = set()
        for item in self.game.player.bullets:
            if c.distance_between_points(item.x, item.y, self.x, self.y) < item.radius + self.radius:
                self.get_hit_by(item)
                to_destroy.add(item)
        self.game.player.bullets -= to_destroy

    def get_hit_by(self, bullet):
        # can't get hit if you're dead
        if self.dead:
            return
        self.hp -= 1
        if self.hp <= 0:
            self.die()

    def is_colliding_with_player(self, player):
        # can't collide if you're dead
        if self.dead:
            return False

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
    HOVERING = 0
    DASHING = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hover_x = c.WINDOW_WIDTH * 0.8

        self.hover_length = 2
        self.x_velocity = 0
        self.hp = 7

        self.value = 10

        self.shiver_x = 0
        self.shiver_y = 0
        self.shiver_target = [1, 0]
        self.shiver_intensity = 0
        self.since_hit = 10
        self.since_particle = 0

        self.state = self.HOVERING

        self.sprite = Sprite(12)
        self.sprite.add_animation({"Hovering": dasher_hovering,
            "Dashing": dasher_dashing,
            "Damage": dasher_damage,
            "DashDamage": dasher_dashing_damage})
        self.sprite.start_animation("Hovering")

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
            self.state = self.DASHING
            self.sprite.start_animation("Dashing")
            self.x_velocity = -1600
            self.x += self.x_velocity * dt
            self.shiver_target = [0, 0]

        self.shiver_x += (self.shiver_target[0] - self.shiver_x) * self.shiver_intensity * dt * 2.5
        self.shiver_y += (self.shiver_target[1] - self.shiver_y) * self.shiver_intensity * dt * 2.5

        self.check_player_bullets()
        if self.hp <= 0:
            self.die()

        self.since_hit += dt
        self.since_particle += dt

        if self.since_hit > 0.04 and self.state == self.HOVERING:
            self.sprite.start_animation("Hovering")
        elif self.since_hit > 0.04 and self.state == self.DASHING:
            self.sprite.start_animation("Dashing")


        if self.since_particle >= 0.02:
            self.game.particles.insert(0, DasherSmokeRed(self.game, self.x, self.y))
            self.game.particles.append(DasherSmoke(self.game, self.x, self.y))
            self.since_particle = 0

        self.sprite.update(dt)

    def draw(self, surface):
        xoff = math.sin(self.age * 5) * 15
        yoff = math.sin(self.age * 7) * 15
        sx, sy = self.game.get_shake_offset()
        x, y = int(self.x + self.shiver_x + sx), int(self.y + self.shiver_y + sy)
        self.sprite.set_position((x + xoff, y + yoff))
        self.sprite.draw(surface)

    def get_hit_by(self, bullet):
        super().get_hit_by(bullet)
        if self.state == self.HOVERING:
            self.sprite.start_animation("Damage")
            self.since_hit = 0
        if self.state == self.DASHING:
            self.sprite.start_animation("DashDamage")
            self.since_hit = 0

    def die(self):
        super().die()
        self.game.shake(6)


class Crawler(Enemy):
    CRAWLING = 0
    LAUNCHING = 1
    DEAD = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.speed = -400
        self.velocity = [0, 0]
        self.launch_speed = 1000
        self.state = self.CRAWLING
        self.radius = 24
        self.y = c.WINDOW_HEIGHT//2 + self.game.corridor.width//2 - self.radius
        self.hp = 2
        self.remove_on_death = False

        self.sprite = Sprite(12)
        self.sprite.add_animation({"Running":crawler_running,
            "Jumping":crawler_jump,
            "Hurt":crawler_hurt,
            "Dead":crawler_dead})
        self.sprite.start_animation("Running")

        self.detect_range = 200
        self.since_hurt = 10
        self.hurt_playing = False
        self.since_land = 10

        self.value = 5

    def get_hit_by(self, bullet):
        super().get_hit_by(bullet)
        if not self.state == self.DEAD:
            self.since_hurt = 0
            self.hurt_playing = True
            self.sprite.start_animation("Hurt")
        if self.state == self.LAUNCHING:
            self.velocity[0] += bullet.dir[0] * 300
            self.velocity[1] += bullet.dir[1] * 300
        elif self.state == self.CRAWLING:
            self.x += 5

    def update(self, dt, events):
        super().update(dt, events)

        dx = self.x - self.game.player.x
        dy = self.y - self.game.player.y
        if dx < self.detect_range and dx > 0 and self.state == self.CRAWLING and self.since_land > 2:
            self.state = self.LAUNCHING
            self.velocity = self.launch_velocity()
            self.sprite.start_animation("Jumping")

        if self.state == self.CRAWLING:
            self.x += self.speed * dt
        elif self.state == self.LAUNCHING:
            self.velocity[1] += 2000*dt
            self.x += self.velocity[0] * dt
            self.y += self.velocity[1] * dt
            if self.y >= c.WINDOW_HEIGHT//2 + self.game.corridor.width//2 - self.radius and self.velocity[1] > 0:
                self.reset_as_floor_crawler()
                self.since_land = 0
                return
        elif self.state == self.DEAD:
            self.velocity[1] += 2000*dt
            self.x += self.velocity[0] * dt
            self.y += self.velocity[1] * dt
            if self.y > c.WINDOW_HEIGHT//2 + self.game.corridor.width//2 - self.radius:
                self.y = c.WINDOW_HEIGHT//2 + self.game.corridor.width//2 - self.radius
                self.velocity[0] = -self.game.scroll_speed


        if self.since_hurt > 0.05 and self.hurt_playing and not self.state == self.DEAD:
            if self.state == self.CRAWLING:
                self.sprite.start_animation("Running")
            elif self.state == self.LAUNCHING:
                self.sprite.start_animation("Jumping")

        if self.y <= c.WINDOW_HEIGHT//2 - self.game.corridor.width//2 + self.radius:
            self.y = c.WINDOW_HEIGHT//2 - self.game.corridor.width//2 + self.radius

        self.since_hurt += dt
        self.since_land += dt

        self.sprite.update(dt)

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
        sx, sy = self.game.get_shake_offset()
        x, y = int(self.x + sx), int(self.y + sy)
        self.sprite.set_position((x, y))
        self.sprite.draw(surface)

    def die(self):
        super().die()
        self.state = self.DEAD
        self.sprite.start_animation("Dead")
        new_y = -300 if self.y < c.WINDOW_HEIGHT//2 - self.game.corridor.width//2 + 200 else -150
        self.velocity = [-random.random() * 200, new_y]

    def reset_as_floor_crawler(self):
        Crawler.__init__(self, self.game, self.x, self.y)
        self.y = c.WINDOW_HEIGHT//2 + self.game.corridor.width//2 - self.radius


class CrawlerCeiling(Crawler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.y = c.WINDOW_HEIGHT//2 - self.game.corridor.width//2 + self.radius
        self.launch_speed = 500
        self.sprite = Sprite(12)
        self.sprite.add_animation({"Running":crawler_running_ceiling,
            "Jumping":crawler_jump,
            "Hurt":crawler_hurt_ceiling,
            "Dead":crawler_dead})
        self.sprite.start_animation("Running")

    def launch_velocity(self):
        if self.y >= c.WINDOW_HEIGHT//2:
            return super().launch_velocity()
        angle = math.pi * 1.25
        angle += (random.random() * math.pi/4) - math.pi/8
        x = math.cos(angle) * self.launch_speed
        y = -math.sin(angle) * self.launch_speed
        return [x, y]
