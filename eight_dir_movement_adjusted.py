"""
Script is identical to eight_dir_move with an adjustment so that the player
moves at the correct speed when travelling at an angle. The script is also
changed to use a time step to update the player. This means that speed is now
in pixels per second, rather than pixels per frame. The advantage of this is
that the game will always update at the same speed, regardless of any frame
loss.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import math
import pygame as pg


SCREEN_SIZE = (500, 500)

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
TRANSPARENT = (0, 0, 0, 0)

DIRECT_DICT = {pg.K_LEFT  : (-1, 0),
               pg.K_RIGHT : ( 1, 0),
               pg.K_UP    : ( 0,-1),
               pg.K_DOWN  : ( 0, 1)}

#X and Y Component magnitude when moving at 45 degree angles
ANGLE_UNIT_SPEED = math.sqrt(2)/2


class Player(object):
    """This class will represent our user controlled character."""
    def __init__(self, speed, *rect):
        """
        Arguments are the player's speed (in pixels/second) and the player's
        rect (all rect style arguments accepted).
        """
        self.rect = pg.Rect(rect)
        self.move = list(self.rect.center)
        self.speed = speed
        self.image = self.make_image()

    def make_image(self):
        """Creates our hero (a red circle/ellipse with a black outline)."""
        image = pg.Surface(self.rect.size).convert_alpha()
        image.fill(TRANSPARENT)
        image_rect = image.get_rect()
        pg.draw.ellipse(image, BLACK, image_rect)
        pg.draw.ellipse(image, RED, image_rect.inflate(-12, -12))
        return image

    def update(self, screen_rect, keys, dt):
        """Updates our player appropriately every frame."""
        vector = [0, 0]
        for key in DIRECT_DICT:
            if keys[key]:
                vector[0] += DIRECT_DICT[key][0]
                vector[1] += DIRECT_DICT[key][1]
        factor = (ANGLE_UNIT_SPEED if all(vector) else 1)
        frame_speed = self.speed*factor*dt
        self.move[0] += vector[0]*frame_speed
        self.move[1] += vector[1]*frame_speed
        self.rect.center = self.move
        if not screen_rect.contains(self.rect):
            self.rect.clamp_ip(screen_rect)
            self.move = list(self.rect.center)

    def draw(self, surface):
        """Draws the player to the target surface."""
        surface.blit(self.image, self.rect)


class Control(object):
    """Keep things under control."""
    def __init__(self):
        """Initializing in the init; how novel."""
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pg.init()
        pg.display.set_caption("Move me with the Arrow Keys.")
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.keys = pg.key.get_pressed()
        self.player = self.make_player()

    def make_player(self):
        """Create a player and set player.move and player.rect.center equal."""
        player = Player(190, (0, 0, 100, 100))
        player.move = list(self.screen_rect.center)
        return player

    def event_loop(self):
        """One event loop. Never cut your game off from the event loop."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True

    def main_loop(self):
        """One game loop. Simple and clean."""
        while not self.done:
            time_delta = self.clock.tick(self.fps)/1000.0
            self.event_loop()
            self.player.update(self.screen_rect, self.keys, time_delta)
            self.screen.fill(WHITE)
            self.player.draw(self.screen)
            pg.display.update()


if __name__ == "__main__":
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
