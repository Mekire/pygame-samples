"""
Demonstrates two different methods of punching a hole in a surface.
I then extend one of the methods in gradient_hole to show more complex effects.
The hole will follow the mouse cursor.  The three different methods are called
in the update function; uncomment the one you would like to test, and comment
out the other two.  Various comments also indicate parameters that you are
encouraged to experiment with.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import pygame as pg


class Control(object):
    """A class to maintain sanity."""
    def __init__(self):
        """This should look pretty familiar."""
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.keys = pg.key.get_pressed()
        self.background = FRACTAL
        self.ellipse_rect = pg.Rect((0,0,400,400))

    def event_loop(self):
        """We don't have much to do here in this one, but it is still essential
        that this runs every frame."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True

    def make_hole(self):
        """This method uses convert() surfaces with a colorkey."""
        hole = pg.Surface(self.screen_rect.size).convert()
        hole.set_colorkey((255,0,255))
        hole.fill((0,0,0)) #Experiment with changing this color.
        pg.draw.ellipse(hole,(255,0,255), self.ellipse_rect)
##        hole.set_alpha(200) #Experiment with uncommenting/changing this value.
        self.screen.blit(hole,(0,0))

    def make_hole_alpha(self):
        """This method uses convert_alpha() and has no need for color keys."""
        hole = pg.Surface(self.screen_rect.size).convert_alpha()
        hole.fill((255,255,255,200)) #Experiment with changing this color
        pg.draw.ellipse(hole,(0,0,0,0), self.ellipse_rect)
        self.screen.blit(hole,(0,0))

    def gradient_hole(self):
        """This method is a modification on the make_hole_alpha method.  It will
        draw a series of ellipses that decrease in size according to step, and
        decrease in alpha according to alpha_step.  This allows us to create
        some fairly simple gradient style effects."""
        hole = pg.Surface(self.screen_rect.size).convert_alpha()
        color = pg.Color(50,0,0,255) #Experiment with changing this color
        hole.fill(color)
        step = (-50,-10) #Change ammount to shrink each rect by
        alpha_step = 40 #Change amount to change transparency per step
        tent_step_amount_x = self.ellipse_rect.width//abs(step[0])
        tent_step_amount_y = self.ellipse_rect.height//abs(step[1])
        number_of_steps = min(tent_step_amount_x,tent_step_amount_y)
        shrink_rect = self.ellipse_rect.copy()
        for i in range(number_of_steps):
            color.a = max(color.a-alpha_step,0)
            pg.draw.ellipse(hole,color,shrink_rect)
            #Inflate should auto-adjust the rect's center,
            #but in the case of a step of -1,-1 it fails.
            shrink_rect.inflate_ip(step)
            shrink_rect.center = self.ellipse_rect.center
        self.screen.blit(hole,(0,0))

    def update(self):
        """Uncomment the version you want to test."""
        self.ellipse_rect.center = pg.mouse.get_pos()
        self.screen.blit(self.background,(0,0))
        self.make_hole()
##        self.make_hole_alpha()
##        self.gradient_hole()

    def main_loop(self):
        """Spin me right round."""
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_mode((1000,650))
    FRACTAL = pg.image.load("frac.jpg").convert()
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
