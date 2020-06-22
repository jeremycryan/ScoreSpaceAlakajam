from scene import Scene
from title_screen import TitleScreen
import constants as c
import pygame


class StoryScene(Scene):

    def next_scene(self):
        return TitleScreen(self.game)

    def main(self):
        clock = pygame.time.Clock()
        scene_count = 0
        scene_1_time = 6.4
        scene_2_time = 6.4
        scene_3_time = 6.4
        age = 0

        scenes = [pygame.image.load("images/lore_1.png"),
            pygame.image.load("images/lore_2.png"),
            pygame.image.load("images/lore_3.png")]

        shade = pygame.Surface(c.WINDOW_SIZE)
        shade.fill(c.BLACK)
        shade.set_alpha(0)

        self.game.battle_music.play()

        for i, item in enumerate(scenes):
            w = item.get_width()
            h = item.get_height()
            scenes[i] = pygame.transform.scale(item, (w*4, h*4))

        while True:
            dt = clock.tick(60)/1000
            events = self.game.update_globals()

            age += dt

            if age > scene_1_time and scene_count == 0:
                scene_count = 1
            if age > scene_1_time + scene_2_time and scene_count == 1:
                scene_count = 2
            if age > scene_1_time + scene_2_time + scene_3_time:
                self.game.battle_music.fadeout(6000)
                shade.set_alpha(255 - 255*(6 - age + (scene_1_time + scene_2_time + scene_3_time))/6)
                if shade.get_alpha() >= 255:
                    break

            self.game.screen.fill(c.BLACK)
            surf = scenes[scene_count]
            self.game.screen.blit(scenes[scene_count], (c.WINDOW_WIDTH//2 - surf.get_width()//2, 120))

            text = c.LORE_TEXT[scene_count]
            words = [self.game.ledger_font.render(word.upper(), 1, c.WHITE) for word in text.split()]
            x = c.WINDOW_WIDTH//2 - surf.get_width()//2
            y = 120 + surf.get_height() + 20
            xoff = 0
            for word in words:
                if xoff + word.get_width() > surf.get_width():
                    xoff = 0
                    y += 25
                self.game.screen.blit(word, (x+xoff, y))
                xoff += word.get_width() + 9

            self.game.screen.blit(shade, (0, 0))
            pygame.display.flip()
        age = 0
        while age < 1:
            dt = clock.tick(60)/1000
            events = self.game.update_globals()
            age += dt
