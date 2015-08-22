#! /usr/bin/env python

"""
A very simple example showing how to drag an item with the mouse.
Dragging in this example uses relative mouse movement.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys

import pygame as pg


CAPTION = "Drag the Red Square"
SCREEN_SIZE = (1000, 600)


class Character(object):
    """
    A class to represent our lovable red sqaure.
    """
    SIZE = (150, 150)
    
    def __init__(self, pos):
        """
        The argument pos corresponds to the center of our rectangle.
        """
        self.rect = pg.Rect((0,0), Character.SIZE)
        self.rect.center = pos
        self.text, self.text_rect = self.setup_font()
        self.click = False

    def setup_font(self):
        """
        If your text doesn't change it is best to render once, rather than
        re-render every time you want the text.  Rendering text every frame is
        a common source of bottlenecks in beginner programs.
        """
        font = pg.font.SysFont('timesnewroman', 30)
        message = "I'm a red square"
        label = font.render(message, True, pg.Color("white"))
        label_rect = label.get_rect()
        return label, label_rect

    def check_click(self, pos):
        """
        This function is called from the event loop to check if a click
        overlaps with the player rect.
        pygame.mouse.get_rel must be called on an initial hit so that
        subsequent calls give the correct relative offset.
        """
        if self.rect.collidepoint(pos):
            self.click = True
            pg.mouse.get_rel()

    def update(self, screen_rect):
        """
        If the square is currently clicked, update its position based on the
        relative mouse movement.  Clamp the rect to the screen.
        """
        if self.click:
            self.rect.move_ip(pg.mouse.get_rel())
            self.rect.clamp_ip(screen_rect)
        self.text_rect.center = (self.rect.centerx, self.rect.centery+90)

    def draw(self, surface):
        """
        Blit image and text to the target surface.
        """
        surface.fill(pg.Color("red"), self.rect)
        surface.blit(self.text, self.text_rect)


class App(object):
    """
    A class to manage our event, game loop, and overall program flow.
    """
    def __init__(self):
        """
        Get a reference to the screen (created in main); define necessary
        attributes; and create our player (draggable rect).
        """
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60
        self.done = False
        self.keys = pg.key.get_pressed()
        self.player = Character(self.screen_rect.center)

    def event_loop(self):
        """
        This is the event loop for the whole program.
        Regardless of the complexity of a program, there should never be a need
        to have more than one event loop.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.player.check_click(event.pos)
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.player.click = False
            elif event.type in (pg.KEYUP, pg.KEYDOWN):
                self.keys = pg.key.get_pressed() 

    def render(self):
        """
        All drawing should be found here.
        This is the only place that pygame.display.update() should be found.
        """
        self.screen.fill(pg.Color("black"))
        self.player.draw(self.screen)
        pg.display.update()

    def main_loop(self):
        """
        This is the game loop for the entire program.
        Like the event_loop, there should not be more than one game_loop.
        """
        while not self.done:
            self.event_loop()
            self.player.update(self.screen_rect)
            self.render()
            self.clock.tick(self.fps)


def main():
    """
    Prepare our environment, create a display, and start the program.
    """
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    App().main_loop()
    pg.quit()
    sys.exit()
    

if __name__ == "__main__":
    main()
