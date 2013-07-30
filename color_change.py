"""
Basics introduction.  Change the screen color with a mouse click.
"""

import os  #used for os.environ
import sys  #used for sys.exit
import pygame as pg  #import the pygame module (I abbreviate it pg for brevity).
from random import randint


class Control(object):
    """A control class to manage our event and game loops."""
    def __init__(self):
        """Get pygame ready and define our start color as black."""
        os.environ['SDL_VIDEO_CENTERED'] = '1'  #Center the screen.
        pg.init() #Initialize Pygame.
        pg.display.set_caption("Click to Change My Color.")
        self.screen = pg.display.set_mode((500,500)) #Set the mode of the screen
        self.clock = pg.time.Clock() #Create a clock to restrict framerate.
        self.fps = 60.0  #Define your max framerate.
        self.done = False #A flag to tell our game when to quit.
        self.keys = pg.key.get_pressed() #All the keys currently held.
        self.color = 0  #The screen will start as black.

    def event_loop(self):
        """Our event loop; called once every frame."""
        for event in pg.event.get(): #Check the events on the event queue
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                #If the user presses escape or closes the window we're done.
                self.done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                #If the user clicks the screen, change the color.
                self.color = [randint(0,255) for i in range(3)]

    def main_loop(self):
        """Our game loop. It calls the event loop; updates the display;
        restricts the framerate; and loops."""
        while not self.done:
            self.event_loop()  #Run the event loop every frame.
            self.screen.fill(self.color) #Fill the screen with the new color.
            pg.display.update()  #Make updates to screen every frame.
            self.clock.tick(self.fps) #Restrict framerate of program.


if __name__ == "__main__":
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
