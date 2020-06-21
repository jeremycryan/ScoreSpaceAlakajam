import pygame
import constants as c
from bullet import Bullet
from sprite_tools import SpriteSheet, Sprite
import math


player_running = SpriteSheet("images/player.png", (1, 1), 1, scale=2)
player_dead = SpriteSheet("images/player_dead.png", (1, 1), 1, scale=2)
player_hit = SpriteSheet("images/player_hit.png", (1, 1), 1, scale=2)


class Player:
    def __init__(self, game):
        self.game = game

        self.width = 64
        self.height = 64

        self.x = c.WINDOW_WIDTH/3
        self.y = c.WINDOW_HEIGHT//2 + self.game.corridor.width//2 - self.height//2

        self.y_velocity = 0
        self.x_velocity = 0

        self.extra_jumps = 1

        self.bullets = set()
        self.bullet_cooldown = 0
        self.bullet_period = 0.10

        self.gunfire = pygame.mixer.Sound("sounds/gunfire.wav")
        self.hurt_noise = pygame.mixer.Sound("sounds/hurt.wav")
        self.death_noise = pygame.mixer.Sound("sounds/death.wav")
        self.hurt_noise.set_volume(0.5)
        self.jump_noise = pygame.mixer.Sound("sounds/jump.wav")

        self.sprite = Sprite(7)
        self.sprite.add_animation({"Running": player_running, "Dead": player_dead, "Hit": player_hit})
        self.sprite.start_animation("Running")
        self.gun = pygame.image.load("images/player_gun.png")
        self.gun = pygame.transform.scale(self.gun, (self.gun.get_width()*2, self.gun.get_height()*2))

        self.since_hit = 10
        self.invincibility_period = 1

        self.movement_enabled = True
        self.in_bus = False

        self.cash = 0
        self.cash_this_level = 0
        self.dead = False

        self.collision_radius = 24
        self.hit_circle_radius = 1000

        self.hp = 3

    def update(self, dt, events):
        if pygame.mouse.get_pressed()[0]:
            self.shoot()

        if self.hit_circle_radius < 1000:
            self.hit_circle_radius += 2500*dt

        if self.movement_enabled:
            self.y_velocity += 2500 * dt
            self.y += self.y_velocity * dt
            self.x_velocity *= 0.0005**dt
            self.x += self.x_velocity * dt
        self.bullet_cooldown += dt
        self.since_hit += dt

        if self.since_hit >= 0.05 and not self.dead:
            self.sprite.start_animation("Running")

        self.collide_corridor(self.game.corridor)
        self.update_movement(dt, events)

        to_destroy = set()
        for bullet in self.bullets:
            bullet.update(dt, events)
            margin = 30
            if bullet.x > c.WINDOW_WIDTH + margin or bullet.y > c.WINDOW_HEIGHT + margin or \
                bullet.x < -margin or bullet.y < -margin:
                to_destroy.add(bullet)
        self.bullets -= to_destroy

        self.sprite.update(dt)

        mindist = 800
        for enemy in self.game.enemies:
            if enemy.dead or self.dead:
                continue
            dist = c.distance_between_points(self.x, self.y, enemy.x, enemy.y)
            dist -= enemy.radius + 32
            if dist < mindist:
                mindist = dist
        if mindist < 0:
            mindist = 0
        self.game.slowdown = min(0.4 + 0.6 * mindist/130, 1)

    def die(self):
        self.game.scroll_speed = 0
        self.dead = True
        self.x_velocity = 500
        self.y_velocity = -1000
        self.sprite.start_animation("Dead")
        self.death_noise.play()

    def update_movement(self, dt, events):
        if not self.movement_enabled:
            return

        pressed = pygame.key.get_pressed()
        if self.on_floor():
            acceleration = 6000
        else:
            acceleration = 3000
        max_speed = 500

        if not self.dead:
            if pressed[pygame.K_a]:
                self.x_velocity -= dt * acceleration
            if pressed[pygame.K_d]:
                self.x_velocity += dt * acceleration
            if pressed[pygame.K_w]:
                if not self.on_floor():
                    self.y_velocity -= 1400*dt

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    if not self.dead:
                        self.jump()

        invisible_force = 40
        if not self.on_floor():
            invisible_force = 20
        if self.x > c.WINDOW_WIDTH*0.5:
            diff = self.x - c.WINDOW_WIDTH*0.4
            self.x_velocity -= invisible_force*diff*dt
        elif self.x < c.WINDOW_WIDTH*0.25:
            diff = c.WINDOW_WIDTH*0.25 - self.x
            self.x_velocity += invisible_force*diff*dt

        if self.x_velocity > max_speed:
            self.x_velocity = max_speed
        if self.x_velocity < -max_speed:
            self.x_velocity = -max_speed

    def jump(self):
        if self.on_floor() or self.extra_jumps > 0:
            self.jump_noise.play()
            self.y_velocity = -660
            if not self.on_floor():
                self.extra_jumps -= 1

    def draw(self, surface):
        sx, sy = self.game.get_shake_offset()
        x, y = int(self.x + sx), int(self.y + sy)
        self.sprite.set_position((x, y))
        self.sprite.draw(surface)

        mpos = pygame.mouse.get_pos()
        dx = mpos[0] - self.x
        dy = mpos[1] - self.y
        angle = -math.atan2(dy, dx) * 180 / math.pi
        if self.dead:
            angle = 0
        gun = pygame.transform.rotate(self.gun, angle)
        gx = x - gun.get_width()//2
        gy = y - gun.get_height()//2 - 14
        surface.blit(gun, (gx, gy))

        if self.hit_circle_radius < 1000:
            pass
            #pygame.draw.circle(surface, c.WHITE, (int(self.x), int(self.y)), int(self.hit_circle_radius+5), 5)

        for bullet in self.bullets:
            bullet.draw(surface)


    def shoot(self):
        if not self.bullet_cooldown > self.bullet_period:
            return
        if self.dead:
            return
        if not self.movement_enabled:
            return

        self.bullet_cooldown = 0

        mpos = pygame.mouse.get_pos()
        dx = mpos[0] - self.x
        dy = mpos[1] - self.y
        mag = (dx**2 + dy**2)**0.5
        dir = (dx/mag, dy/mag)
        new_bullet = Bullet(self.game, self.x, self.y, dir)
        self.bullets.add(new_bullet)

        recoil = 80
        self.game.shake(3)
        self.x_velocity -= recoil * dir[0]
        if not self.on_floor():
            self.y_velocity -= recoil * dir[1]

        self.gunfire.play()

    def on_floor(self):
        off = self.height//3
        if self.y >= c.WINDOW_HEIGHT//2 + self.game.corridor.width//2 - off:
            self.extra_jumps = 1
            return True
        return False

    def collide_corridor(self, corridor):
        off = self.height//3
        if self.y + off > c.WINDOW_HEIGHT//2 + corridor.width//2:
            self.y = c.WINDOW_HEIGHT//2 + corridor.width//2 - off
            self.y_velocity = 0
        elif self.y - off < c.WINDOW_HEIGHT//2 - corridor.width//2:
            self.y = c.WINDOW_HEIGHT//2 - corridor.width//2 + off
            self.y_velocity = 0

    def get_hit_by(self, enemy):
        if self.in_bus == True:
            return
        if self.since_hit < self.invincibility_period:
            return
        self.game.shake(25)
        self.since_hit = 0
        self.hp -= 1
        self.game.flash_alpha = 100
        self.game.slowdown = 0.1
        if self.hp == 0:
            self.game.flash_alpha = 255
            self.die()
        else:
            self.hurt_noise.play()
            self.hit_circle_radius = 0
            pickups = self.game.pickups[:]
            for enemy in self.game.enemies:
                enemy.die()
            self.game.pickups = pickups
            dx = self.x - enemy.x
            dy = self.y - enemy.y
            dx, dy = dx/(abs(dx) + abs(dy)), dy/(abs(dx) + abs(dy))
            self.x_velocity += dx * 1000
            self.y_velocity += dy * 1000
            enemy.velocity[0] -= dx*1000
            enemy.velocity[1] -= dy*1000
            self.sprite.start_animation("Hit")
