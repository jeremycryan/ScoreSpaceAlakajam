import pygame
import sys
import constants as c
from scene import *
import math
import time

from title_screen import TitleScreen
from lose_screen import LoseScreen
from high_scores import HighScores
from story_scene import StoryScene


class Game:
    def __init__(self):
        pygame.mixer.init(44100, -16, 2, 2048)
        pygame.init()
        self.screen = pygame.display.set_mode(c.WINDOW_SIZE)
        self.corridor = Corridor(self)
        self.player = Player(self)
        self.enemies = []
        self.pickups = []
        self.particles = []
        self.scroll_speed = 350
        self.shake_amp = 0
        self.shake_period = 0
        self.level = 1
        self.ledger_font = pygame.font.Font("fonts/Pixeled.ttf", 10)
        self.score_font = pygame.font.Font("fonts/Pixeled.ttf", 20)
        self.score = 0
        self.name = "User" + str(int(random.random()*100))
        self.slowdown = 1.0
        self.target_slowdown = 1.0
        self.flash_alpha = 0
        self.first_play = True
        pygame.display.set_caption("Public Transit Battle Corgi Tycoon")
        self.battle_music = pygame.mixer.Sound("sounds/battle_corgi.wav")
        self.battle_music.set_volume(0.8)
        self.bus_ride = pygame.mixer.Sound("sounds/bus_ride.wav")
        self.bus_ride.set_volume(0.8)
        self.bullet_impact = pygame.mixer.Sound("sounds/bullet_impact.wav")
        self.pickup_sound = pygame.mixer.Sound("sounds/cash_pickup.wav")
        self.press_enter = pygame.mixer.Sound("sounds/press_enter.wav")
        self.press_enter.set_volume(0.4)
        self.pickup_sound.set_volume(0.5)
        self.muffled_train = pygame.mixer.Sound("sounds/muffled_train.wav")
        self.door_close = pygame.mixer.Sound("sounds/door_close.wav")
        self.nope = pygame.mixer.Sound("sounds/nope.wav")
        self.door_close.set_volume(0.3)
        self.main()

    def update_screenshake(self, dt, events):
        self.shake_period += dt
        self.shake_amp *= 0.05**dt
        self.shake_amp = max(0, self.shake_amp - 30*dt)

    def update_slowdown(self, dt, events):
        if self.target_slowdown > self.slowdown:
            self.slowdown = min(self.target_slowdown, self.slowdown + dt)
        elif self.target_slowdown < self.slowdown:
            self.slowdown = max(self.target_slowdown, self.slowdown - dt)

    def shake(self, amp):
        self.shake_amp = max(self.shake_amp, amp)
        self.shake_period = 0

    def get_shake_offset(self):
        x = self.shake_amp * math.cos(time.time() * 30)
        y = self.shake_amp * math.cos(time.time() * 24)
        return x, y

    def update_globals(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        return events

    def main(self):
        current_scene = StoryScene(self)
        while True:
            current_scene.main()
            current_scene = current_scene.next_scene()
            time.sleep(0.2)



if __name__=="__main__":
    Game()
