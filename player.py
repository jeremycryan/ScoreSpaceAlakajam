import pygame
import constants as c
from bullet import Bullet


class Player:
    def __init__(self, game):
        self.game = game

        self.width = 48
        self.height = 48

        self.x = c.WINDOW_WIDTH/4
        self.y = c.WINDOW_HEIGHT//2 + self.game.corridor.width//2 - self.height//2

        self.y_velocity = 0
        self.x_velocity = 0

        self.extra_jumps = 1

        self.bullets = set()
        self.bullet_cooldown = 0
        self.bullet_period = 0.10

        self.surf = pygame.Surface((self.width, self.height))

        self.since_hit = 10
        self.invincibility_period = 1

    def update(self, dt, events):
        if pygame.mouse.get_pressed()[0]:
            self.shoot()

        self.y_velocity += 2500 * dt
        self.y += self.y_velocity * dt
        self.x_velocity *= 0.0005**dt
        self.x += self.x_velocity * dt
        self.bullet_cooldown += dt
        self.since_hit += dt

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

    def update_movement(self, dt, events):
        pressed = pygame.key.get_pressed()
        if self.on_floor():
            acceleration = 6000
        else:
            acceleration = 3000
        max_speed = 500

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
                    self.jump()

        invisible_force = 40
        if not self.on_floor():
            invisible_force = 20
        if self.x > c.WINDOW_WIDTH*0.4:
            diff = self.x - c.WINDOW_WIDTH*0.4
            self.x_velocity -= invisible_force*diff*dt
        elif self.x < c.WINDOW_WIDTH*0.3:
            diff = c.WINDOW_WIDTH*0.25 - self.x
            self.x_velocity += invisible_force*diff*dt

        if self.x_velocity > max_speed:
            self.x_velocity = max_speed
        if self.x_velocity < -max_speed:
            self.x_velocity = -max_speed

    def jump(self):
        if self.on_floor() or self.extra_jumps > 0:
            self.y_velocity = -660
            if not self.on_floor():
                self.extra_jumps -= 1

    def draw(self, surface):
        surf = self.surf
        if self.on_floor():
            surf.fill(c.BLUE)
        elif self.extra_jumps == 0:
            surf.fill(c.RED)
        else:
            surf.fill(c.GREEN)
        sx, sy = self.game.get_shake_offset()
        x, y = int(self.x + sx), int(self.y + sy)
        surface.blit(surf, (x - self.width//2, y - self.height//2))

        for bullet in self.bullets:
            bullet.draw(surface)

    def shoot(self):
        if not self.bullet_cooldown > self.bullet_period:
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

    def on_floor(self):
        if self.y >= c.WINDOW_HEIGHT//2 + self.game.corridor.width//2 - self.height//2:
            self.extra_jumps = 1
            return True
        return False

    def collide_corridor(self, corridor):
        if self.y + self.height//2 > c.WINDOW_HEIGHT//2 + corridor.width//2:
            self.y = c.WINDOW_HEIGHT//2 + corridor.width//2 - self.height//2
            self.y_velocity = 0
        elif self.y - self.height//2 < c.WINDOW_HEIGHT//2 - corridor.width//2:
            self.y = c.WINDOW_HEIGHT//2 - corridor.width//2 + self.height//2
            self.y_velocity = 0

    def get_hit_by(self, enemy):
        if self.since_hit < self.invincibility_period:
            return
        self.game.shake(25)
        self.since_hit = 0
