"""
A very simple example showing how to drag an item with the mouse.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import pygame as pg


SCREEN_SIZE = (1000,600)


class Character(object):
    """A class to represent our lovable red sqaure."""
    def __init__(self,*rect_style_args):
        """Accepts arguments in all the same forms a pygame.Rect would."""
        self.rect = pg.Rect(rect_style_args)
        self.text,self.text_rect = self.setup_font()
        self.click = False

    def setup_font(self):
        """If your text doesn't change it is best to render once, rather than
        rerender every time you want the text."""
        font = pg.font.SysFont('timesnewroman', 30)
        message = "I'm a red square"
        label = font.render(message, True, pg.Color("white"))
        label_rect = label.get_rect()
        return label,label_rect

    def update(self,screen_rect):
        """If the square is currently clicked, update its position based on the
        relative mouse movement."""
        if self.click:
            self.rect.move_ip(pg.mouse.get_rel())
            self.rect.clamp_ip(screen_rect)
        self.text_rect.center = (self.rect.centerx,self.rect.centery+90)

    def draw(self,surface):
        """Blit image and text to the target surface."""
        surface.fill(pg.Color("red"),self.rect)
        surface.blit(self.text,self.text_rect)


class Control(object):
    """A control class to manage our event and game loops."""
    def __init__(self):
        """Here we have set up the pygame session within the init. Sometimes it
        is more convenient to do this elsewhere."""
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pg.init()
        pg.display.set_caption("Drag the Red Square")
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.keys = pg.key.get_pressed()
        self.player = Character(0,0,150,150)
        self.player.rect.center = self.screen_rect.center

    def event_loop(self):
        """This is the event loop for the whole program.  Regardless of the
        complexity of a program, there should never be a need to have more than
        one event loop."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.player.rect.collidepoint(event.pos):
                    self.player.click = True
                    pg.mouse.get_rel()
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.player.click = False

    def main_loop(self):
        """This is the game loop for the entire program.  Like the event_loop,
        there should not be more than one game_loop.  This is the only place
        that pygame.display.update() should be found."""
        while not self.done:
            self.event_loop()
            self.player.update(self.screen_rect)
            self.screen.fill(pg.Color("black"))
            self.player.draw(self.screen)
            pg.display.update()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
