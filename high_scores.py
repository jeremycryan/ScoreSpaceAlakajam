from title_screen import TitleScreen
from scene import Scene
import pygame
import constants as c
from sprocket import Sprocket
import time
import math
import threading
import random
import requests
import constants as c
import scoreboard

class HighScores(Scene):
    def __init__(self, game):
        super().__init__(game)

    def make_sprocket(self):
        while self.sprocket == None:
            try:
                print("Get port url...")
                r = requests.get(c.PORT_URL)
                port = int(r.text.strip())
                print("Establish connection...")
                self.sprocket = Sprocket("0.tcp.ngrok.io", int(port))
                print("Submit score...")
                self.sprocket.send(type="push", name=self.game.name, score=self.game.score)
                print("Fetch scoreboard...")
                self.sprocket.send(type="print")
            except Exception as e:
                with open("error_log.txt", "a") as f:
                    f.write(str(e))
                    f.write("\n\n")
                    print(e)
                break

    def main(self):
        if not self.game.score:
            self.game.score = 0
        if not self.game.name:
            self.game.name = "Empty"
        self.game.name = self.game.name.strip()
        if self.game.name.upper() == "HIM":
            self.game.name = "smartass"

        clock = pygame.time.Clock()
        self.game.bus_ride.play(-1)
        self.sprocket = None

        a = threading.Thread(target=self.make_sprocket, daemon=True)
        a.start()

        self.age = 0
        scores = None

        packets = []
        do_break = False
        self.refresh = False

        while True:
            dt = clock.tick(60)/1000
            events = self.game.update_globals()
            self.age += dt

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        do_break = True
                    if event.key == pygame.K_r:
                        do_break = True
                        self.refresh = True
            if do_break:
                self.game.bus_ride.fadeout(100)
                self.game.press_enter.play()
                break

            if self.sprocket is not None:
                if not packets and not scores:
                    packets = self.sprocket.get()
                elif not scores:
                    scores = packets[0].scores.data[:20]

            self.game.screen.fill(c.BLACK)
            line_width = c.WINDOW_WIDTH//3
            y = 35
            x = c.WINDOW_WIDTH//2 - line_width//2
            surf = self.game.score_font.render("HIGH SCORES", 1, c.WHITE)
            self.game.screen.blit(surf, (x + line_width//2 - surf.get_width()//2, y + 4*math.sin(time.time()*math.pi * 4)))
            y += 70

            found = False
            if scores:
                for i, item in enumerate(scores):

                    name = item.name[:12]
                    score = float(item.score)
                    if name.upper() == self.game.name.upper() and score == self.game.score and not found:
                        color = c.GREEN
                        found = True
                    else:
                        color = c.WHITE
                    surf = self.game.ledger_font.render(str(name).upper(), 1, color)
                    self.game.screen.blit(surf, (x, y))
                    surf = self.game.ledger_font.render(str(round(score, 1)) + "0", 1, color)
                    self.game.screen.blit(surf, (x + line_width - surf.get_width(), y))
                    y += surf.get_height() * 0.7
            else:
                dots = 1 + int((time.time()*3)%3)
                text = "LOADING" + dots*"."
                color = (180, 180, 180)
                if self.age > 10:
                    text = "PRESS R TO RETRY LOADING."
                    color = (255, 100, 100)
                surf = self.game.ledger_font.render(text, 1, color)
                self.game.screen.blit(surf, (c.WINDOW_WIDTH//2 - surf.get_width()//2, c.WINDOW_HEIGHT//2))

            if time.time()%1 < 0.7:
                surf = self.game.ledger_font.render("PRESS ENTER TO OKAY", 1, c.WHITE)
                self.game.screen.blit(surf, (c.WINDOW_WIDTH//2 - surf.get_width()//2, c.WINDOW_HEIGHT - 60))
            pygame.display.flip()


    def next_scene(self):
        if self.refresh:
            return HighScores(self.game)
        return TitleScreen(self.game)
