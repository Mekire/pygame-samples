"""
This example shows scrolling a topdown map when the mouse nears the edges of
the screen.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import pygame as pg


CAPTION = "Scrolling Background"
SCREEN_SIZE = (500, 500)

DIRECT_DICT = {"DOWN" : ( 0, 1),
               "UP"   : ( 0,-1),
               "LEFT" : (-1, 0),
               "RIGHT": ( 1, 0)}


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
        self.controls = {pg.K_DOWN : "DOWN",
                         pg.K_UP   : "UP",
                         pg.K_LEFT : "LEFT",
                         pg.K_RIGHT: "RIGHT"}

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
        for key in self.controls:
            if keys[key]:
                direction = self.controls[key]
                vector = DIRECT_DICT[direction]
                for i in (0, 1):
                    move[i] += vector[i]*self.speed
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
        self.scroll_rects = self.make_scroll_rects()
        self.scroll_speed = 5

    def make_scroll_rects(self):
        """
        The map will scroll in the appropriate direction if inside any of
        these rects.
        """
        rects = {"UP"   : pg.Rect(0, 0, self.viewport.w, 20),
                 "DOWN" : pg.Rect(0, self.viewport.h-20, self.viewport.w, 20),
                 "LEFT" : pg.Rect(0, 0, 20, self.viewport.h),
                 "RIGHT": pg.Rect(self.viewport.w-20, 0, 20, self.viewport.h)}
        return rects

    def update(self, keys):
        """
        Updates the player and then adjust the viewport with respect to the
        player's new position.
        """
        self.player.update(self.mask, keys)
        self.update_viewport()

    def update_viewport(self):
        """
        The viewport scrolls if the mouse is in any of the scroll rects.
        """
        mouse = pg.mouse.get_pos()
        for direct,rect in self.scroll_rects.items():
            if rect.collidepoint(mouse):
                self.viewport.x += DIRECT_DICT[direct][0]*self.scroll_speed
                self.viewport.y += DIRECT_DICT[direct][1]*self.scroll_speed
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
        #Scroll rects filled for better visualization.
        for rect in self.scroll_rects.values():
            temp = pg.Surface(rect.size).convert_alpha()
            temp.fill((0,0,0,100))
            surface.blit(temp, rect)


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
        self.level.viewport.center = self.level.rect.center

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
