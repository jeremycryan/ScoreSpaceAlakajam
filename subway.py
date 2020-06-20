import pygame
import constants as c
import random


class Subway:
    def __init__(self, game):
        self.game = game
        self.x = -200
        self.y = 270
        self.car = pygame.image.load("images/subway_car_no_door.png")
        self.door_left = pygame.image.load("images/subway_car_left_door.png")
        self.door_right = pygame.image.load("images/subway_car_right_door.png")

        self.accel = 1200
        self.moving = False
        self.speed = 0
        self.age = 0
        self.length = 4

        self.shake_intensity = 2
        self.shake_target = [0, 0]
        self.shake_position = [0, 0]

        self.doors_open = 1.0
        self.door_hole = pygame.Surface((112, 180))
        self.door_hole.fill((255, 252, 209))
        self.door_speed = 0

    def update(self, dt, events):
        self.age += dt
        if self.age >= 0.2:
            self.door_speed -= dt * 10
        self.doors_open = min(max(0, self.doors_open + self.door_speed*dt), 1)
        if self.age >= 3:
            self.moving = True
        self.x -= self.game.scroll_speed * dt

        if self.moving:
            if c.distance_between_points(*self.shake_target, *self.shake_position) < 5:
                self.shake_position = [random.random() * 2 - 1, random.random() * 2 - 1]
            dx = self.shake_target[0] - self.shake_position[0]
            dy = self.shake_target[1] - self.shake_position[1]
            self.shake_position[0] += dx * 2
            self.shake_position[1] += dy * 2
            self.speed += self.accel * dt
            self.x += self.speed * dt
        pass

    def get_my_offset(self):
        return self.shake_position[0] * self.shake_intensity, self.shake_position[1] * self.shake_intensity

    def draw(self, surface):
        msx, msy = self.get_my_offset()
        sx, sy = self.game.get_shake_offset()
        for i in range(self.length):

            if self.x + msx + sx >= c.WINDOW_WIDTH or self.x + msx + sx <= -c.WINDOW_WIDTH:
                msx -= self.car.get_width() + 30
                continue

            surface.blit(self.door_hole, (self.x + sx + msx + 423, self.y + sy + msy + 62))
            open_amt = 40
            if i == 0:
                doff = int(open_amt * self.doors_open)
            else:
                doff = 0
            surface.blit(self.door_left, (self.x + sx + msx + 431 - doff, self.y + sy + msy + 68))
            surface.blit(self.door_right, (self.x + sx + msx + 431 + self.door_left.get_width() + doff, self.y + sy + msy + 68))
            surface.blit(self.car, (self.x + sx + msx, self.y + sy + msy))

            msx -= self.car.get_width() + 30

    def is_visible(self):
        if self.x <= c.WINDOW_WIDTH and self.x > - c.WINDOW_WIDTH:
            return True
        return False


class EndSubway(Subway):
    def __init__(self, game, position):
        super().__init__(game)
        self.x = position

    def update(self, dt, events):
        self.age += dt
        self.doors_open = min(max(0, self.doors_open + self.door_speed*dt), 1)
        self.x -= self.game.scroll_speed * dt
        if self.x <= c.WINDOW_WIDTH:
            self.game.scroll_speed = min(self.game.scroll_speed, (self.x + 430 - c.WINDOW_WIDTH/3))

        if self.moving:
            if c.distance_between_points(*self.shake_target, *self.shake_position) < 5:
                self.shake_position = [random.random() * 2 - 1, random.random() * 2 - 1]
            dx = self.shake_target[0] - self.shake_position[0]
            dy = self.shake_target[1] - self.shake_position[1]
            self.shake_position[0] += dx * 2
            self.shake_position[1] += dy * 2
            self.speed += self.accel * dt
            self.x += self.speed * dt
