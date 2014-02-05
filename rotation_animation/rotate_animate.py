"""
Showing the rotation of an animated body.

-Sean McKiernan.
"""

import os
import sys
import pygame as pg


SCREEN_SIZE = (500, 500)
BACKGROUND_COLOR = (20, 20, 50)
CAPTION = "Rotation Animation"


class Asteroid(pg.sprite.Sprite):
    """A class for an animated spinning asteroid."""
    rotation_cache = {}
    def __init__(self, location, frame_speed=50, angular_speed=0):
        """
        The argument location is the center point of the asteroid;
        frame_speed is the speed in frames per second; angular_speed is the
        rotation speed in degrees per second.
        """
        pg.sprite.Sprite.__init__(self)
        self.frame = 0
        self.frames = self.get_frames(ASTEROID, (96,80), 21, 7, missing=4)
        self.last_frame_info = None
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect(center=location)
        self.animate_fps = frame_speed
        self.angle = 0.0
        self.angular_speed = angular_speed  #Degrees per second.

    def get_frames(self, sheet,size, columns, rows, missing=0):
        """
        Creates a list of all our frames. Fun divmod trick. The missing
        argument specifies how many empty cells (if any) there are on the
        bottom row.
        """
        total = rows*columns-missing
        frames = []
        for frame in range(total):
            y,x = divmod(frame, columns)
            frames.append(sheet.subsurface((x*size[0],y*size[1]),size))
        return frames

    def get_image(self, cache=True):
        """
        Get a new image if either the frame or angle has changed. If cache
        is True the image will be placed in the rotation_cache. This can
        greatly improve speed but is only feasible if caching all the images
        would not cause memory issues.
        """
        frame_info = angle, frame = (int(self.angle), int(self.frame))
        if frame_info != self.last_frame_info:
            if frame_info in Asteroid.rotation_cache:
                image = Asteroid.rotation_cache[frame_info]
            else:
                raw = self.frames[frame]
                image = pg.transform.rotozoom(raw, angle, 1.0)
                if cache:
                    Asteroid.rotation_cache[frame_info] = image
            self.last_frame_info = frame_info
        else:
            image = self.image
        return image

    def update(self,dt):
        """Change the angle and fps based on a time delta."""
        self.angle = (self.angle+self.angular_speed*dt)%360
        self.frame = (self.frame+self.animate_fps*dt)%len(self.frames)
        self.image = self.get_image(False)
        self.rect = self.image.get_rect(center=self.rect.center)


class Control(object):
    """Game loop and event loop found here."""
    def __init__(self):
        """Prepare the essentials and setup an asteroid group."""
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.done = False
        self.keys = pg.key.get_pressed()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.asteroids = self.make_asteroids()

    def make_asteroids(self):
        """
        Arbitrary method that creates a group with four asteroids.
        A static; a rotating; an animating; and a rotating-animating one.
        """
        location_one = [loc//4 for loc in self.screen_rect.size]
        location_two = [loc*3 for loc in location_one]
        location_three = [location_two[0], location_one[1]]
        location_four = [location_one[0], location_two[1]]
        asteroids = [Asteroid(location_one, 0, 0),
                     Asteroid(location_two, 50, 200),
                     Asteroid(location_three, 0, 200),
                     Asteroid(location_four)]
        return pg.sprite.Group(asteroids)

    def event_loop(self):
        """Bare bones event loop."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            self.done = event.type == pg.QUIT or self.keys[pg.K_ESCAPE]

    def display_fps(self):
        """Show the program's FPS in the window handle."""
        caption = "{} - FPS: {:.2f}".format(CAPTION, self.clock.get_fps())
        pg.display.set_caption(caption)

    def main_loop(self):
        """Clean main game loop."""
        delta = 0
        while not self.done:
            self.event_loop()
            self.asteroids.update(delta)
            self.screen.fill(BACKGROUND_COLOR)
            self.asteroids.draw(self.screen)
            pg.display.update()
            delta = self.clock.tick(self.fps)/1000.0
            self.display_fps()


def main():
    """Initialize; load image; and start program."""
    global ASTEROID
    pg.init()
    os.environ["SDL_VIDEO_CENTERED"] = "TRUE"
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    ASTEROID = pg.image.load("asteroid_simple.png").convert_alpha()
    Control().main_loop()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
