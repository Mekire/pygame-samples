#! /usr/bin/env python

"""
This example serves as a basics introduction.
Change the screen color with a mouse click.

This program is intentionally over-commented to serve as an introduction for
those with no knowledge of pygame. More advanced examples will not adhere to
this convention.

-Written by Sean J. McKiernan 'Mekire'
"""

import os # Used for os.environ.
import sys # Used for sys.exit.
import random # Used for random.randint.

import pygame as pg # I abbreviate pygame as pg for brevity.


CAPTION = "Click to Change My Color"
SCREEN_SIZE = (500, 500)


class App(object):
    """
    This is the main class for our application.
    It manages our event and game loops.
    """
    def __init__(self):
        """
        Get a reference to the screen (created in main); define necessary
        attributes; and set our starting color to black.
        """
        self.screen = pg.display.get_surface() # Get reference to the display.
        self.clock = pg.time.Clock() # Create a clock to restrict framerate.
        self.fps = 60 # Define your max framerate.
        self.done = False # A flag to tell our game when to quit.
        self.keys = pg.key.get_pressed() # All the keys currently held.
        self.color = pg.Color("black") # The screen will start as black.

    def event_loop(self):
        """
        Our event loop; called once every frame.  Only things relevant to
        processing specific events should be here.  It should not
        contain any drawing/rendering code.
        """
        for event in pg.event.get():  # Check each event in the event queue.
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                # If the user presses escape or closes the window we're done.
                self.done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                # If the user clicks the screen, change the color.
                self.color = [random.randint(0, 255) for _ in range(3)]
            elif event.type in (pg.KEYUP, pg.KEYDOWN):
                # Update keys when a key is pressed or released.
                self.keys = pg.key.get_pressed() 

    def main_loop(self):
        """
        Our game loop. It calls the event loop; updates the display;
        restricts the framerate; and loops.
        """
        while not self.done:
            self.event_loop() # Run the event loop every frame.
            self.screen.fill(self.color) # Fill the screen with the new color.
            pg.display.update() # Make updates to screen every frame.
            self.clock.tick(self.fps) # Restrict framerate of program.


def main():
    """
    Prepare our environment, create a display, and start the program.
    """
    os.environ['SDL_VIDEO_CENTERED'] = '1' # Center the window (optional).
    pg.init() # Initialize Pygame.
    pg.display.set_caption(CAPTION) # Set the caption for the window.
    pg.display.set_mode(SCREEN_SIZE) # Prepare the screen.
    App().main_loop()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
