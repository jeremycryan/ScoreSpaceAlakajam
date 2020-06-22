import pygame
from scene import Scene
from scene import Controls
import constants as c
from sprite_tools import Sprite, SpriteSheet

class NameHim(Scene):
    def __init__(self, game):
        super().__init__(game)

    def main(self):
        name_him = SpriteSheet("images/name_him.png", (2, 1), 2)
        sprite = Sprite(4)
        sprite.add_animation({"Name Him": name_him})
        sprite.start_animation("Name Him")
        string = ""
        clock = pygame.time.Clock()
        do_break = False
        shade = pygame.Surface(c.WINDOW_SIZE)
        shade.fill(c.BLACK)
        shade_alpha = 255
        shade.set_alpha(shade_alpha)
        while True:

            dt = clock.tick(60)/1000
            if dt > 1/30:
                dt = 1/30
            events = self.game.update_globals()

            speed = 1000
            if do_break:
                if shade_alpha >= 255:
                    self.game.name = string
                    break
                shade_alpha += speed * dt
            else:
                shade_alpha = max(0, shade_alpha - speed * dt)
            shade.set_alpha(shade_alpha)

            self.game.update_screenshake(dt, events)


            self.game.screen.fill(c.BLACK)

            sx, sy = self.game.get_shake_offset()
            sprite.set_position((c.WINDOW_WIDTH//2 + sx, c.WINDOW_HEIGHT//2 + sy))
            sprite.draw(self.game.screen)
            sprite.update(dt)

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        string = string[:-1]
                        self.game.pickup_sound.play()
                    elif event.key == pygame.K_RETURN and not do_break and len(string):
                        do_break = True
                        self.game.press_enter.play()
                    else:
                        char = str(event.unicode)
                        char = char.upper()
                        if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ " and len(string) < 12:
                            string += char
                            self.game.pickup_sound.play()
                        else:
                            self.game.nope.play()
                            self.game.shake(5)

            surf = self.game.score_font.render(string, 1, c.WHITE)
            self.game.screen.blit(surf, (c.WINDOW_WIDTH//2 - surf.get_width()//2 + sx, 400 + sy))
            self.game.screen.blit(shade, (0, 0))

            pygame.display.flip()

    def next_scene(self):
        return Controls(self.game)
