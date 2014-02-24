"""
This example shows a method of making a player stay centered on a scrolling
map. When the player moves close to the edges of the map he will move off
center. This implementation does not employ a tiled map (though the centering
technique works identically). Using a single mask for collision of the entire
level is not an efficient technique. This example is designed to show
viewport centering; not efficient collision.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import pygame as pg


CAPTION = "Scrolling Background"
SCREEN_SIZE = (500, 500)


DIRECT_DICT = {pg.K_UP   : ( 0,-1),
               pg.K_DOWN : ( 0, 1),
               pg.K_RIGHT: ( 1, 0),
               pg.K_LEFT : (-1, 0)}


class Player(object):
    """Our user controllable character."""
    def __init__(self, image, location, speed):
        """
        The location is an (x,y) coordinate; speed is in pixels per frame.
        The location of the player is with respect to the map he is in; not the
        display screen.
        """
        self.speed = speed
        self.image = image
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=location)

    def update(self, level_mask, keys):
        """
        Check pressed keys to find initial movement vector.  Then call
        collision detection methods and adjust the vector appropriately.
        """
        move = self.check_keys(keys)
        self.check_collisions(move, level_mask)

    def check_keys(self, keys):
        """Find the players movement vector from key presses."""
        move = [0, 0]
        for key in DIRECT_DICT:
            if keys[key]:
                for i in (0, 1):
                    move[i] += DIRECT_DICT[key][i]*self.speed
        return move

    def check_collisions(self, move, level_mask):
        """
        Call collision_detail for the x and y components of our movement vector.
        """
        x_change = self.collision_detail(move, level_mask, 0)
        self.rect.move_ip((x_change,0))
        y_change = self.collision_detail(move, level_mask, 1)
        self.rect.move_ip((0,y_change))

    def collision_detail(self, move, level_mask, index):
        """
        Check for collision and if found decrement vector by single pixels
        until clear.
        """
        test_offset = list(self.rect.topleft)
        test_offset[index] += move[index]
        while level_mask.overlap_area(self.mask, test_offset):
            move[index] += (1 if move[index]<0 else -1)
            test_offset = list(self.rect.topleft)
            test_offset[index] += move[index]
        return move[index]

    def draw(self, surface):
        """Basic draw function."""
        surface.blit(self.image, self.rect)


class Level(object):
    """
    A class for our map. Maps in this implementation are one image; not
    tile based. This makes collision detection simpler but can have performance
    implications.
    """
    def __init__(self, map_image, viewport, player):
        """
        Takes an image from which to make a mask, a viewport rect, and a
        player instance.
        """
        self.image = map_image
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.player = player
        self.player.rect.center = self.rect.center
        self.viewport = viewport

    def update(self, keys):
        """
        Updates the player and then adjust the viewport with respect to the
        player's new position.
        """
        self.player.update(self.mask, keys)
        self.update_viewport()

    def update_viewport(self):
        """
        The viewport will stay centered on the player unless the player
        approaches the edge of the map.
        """
        self.viewport.center = self.player.rect.center
        self.viewport.clamp_ip(self.rect)

    def draw(self, surface):
        """
        Blit actors onto a copy of the map image; then blit the viewport
        portion of that map onto the display surface.
        """
        new_image = self.image.copy()
        self.player.draw(new_image)
        surface.fill((50,255,50))
        surface.blit(new_image, (0,0), self.viewport)


class Control(object):
    """We meet again."""
    def __init__(self):
        """Initialize things; create a Player; create a Level."""
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.keys = pg.key.get_pressed()
        self.done = False
        self.player = Player(PLAY_IMAGE, (0,0), 7)
        self.level = Level(POND_IMAGE, self.screen_rect.copy(), self.player)

    def event_loop(self):
        """A quiet day in the neighborhood here."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True

    def display_fps(self):
        """Show the program's FPS in the window handle."""
        caption = "{} - FPS: {:.2f}".format(CAPTION, self.clock.get_fps())
        pg.display.set_caption(caption)

    def update(self):
        """
        Update the level. In this implementation player updating is taken
        care of by the level update function.
        """
        self.screen.fill(pg.Color("black"))
        self.level.update(self.keys)
        self.level.draw(self.screen)

    def main_loop(self):
        """...and we run in circles."""
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)
            self.display_fps()


def main():
    """Initialize, load our images, and run the program."""
    global PLAY_IMAGE, POND_IMAGE
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    PLAY_IMAGE = pg.image.load("smallface.png").convert_alpha()
    POND_IMAGE = pg.image.load("pond.png").convert_alpha()
    Control().main_loop()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
