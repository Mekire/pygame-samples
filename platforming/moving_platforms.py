"""
Basic moving platforms using only rectangle collision.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import pygame as pg


CAPTION = "Moving Platforms"


class _Physics(object):
    """A simplified physics class. Psuedo-gravity is often good enough."""
    def __init__(self):
        """You can experiment with different gravity here."""
        self.x_vel = self.y_vel = 0
        self.grav = 0.22
        self.fall = False

    def physics_update(self):
        """If the player is falling, add gravity to the current y velocity."""
        if self.fall:
            self.y_vel += self.grav
        else:
            self.y_vel = 0


class Player(_Physics,pg.sprite.Sprite):
    """Class representing our player."""
    def __init__(self,location,speed):
        """The location is an (x,y) coordinate pair, and speed is the player's
        speed in pixels per frame. Speed should be an integer."""
        _Physics.__init__(self)
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((30,55)).convert()
        self.image.fill(pg.Color("red"))
        self.rect = self.image.get_rect(topleft=location)
        self.speed = speed
        self.jump_power = -8.0
        self.on_moving = False
        self.collide_below = False

    def get_position(self,obstacles):
        """Calculate where our player will end up this frame including
        collisions."""
        if not self.fall:
            self.check_falling(obstacles)
        else:
            self.fall = self.check_collisions((0,self.y_vel),1,obstacles)
        if self.x_vel:
            self.check_collisions((self.x_vel,0),0,obstacles)

    def check_falling(self,obstacles):
        """Checks one pixel below the player to see if the player is still on
        the ground."""
        if not self.collide_below:
            self.fall = True
            self.on_moving = False

    def check_moving(self,obstacles):
        """Check if the player is standing on a moving platform."""
        if not self.fall:
            self.rect.move_ip((0,1))
            self.collide_below = pg.sprite.spritecollide(self,obstacles,False)
            for collide in self.collide_below:
                if collide.type == "moving":
                    self.on_moving = collide
            self.rect.move_ip((0,-1))

    def check_collisions(self,offset,index,obstacles):
        """This function checks if a collision would occur after moving offset
        pixels.  If a collision is detected position is decremented by one pixel
        and retested. This continues until we find exactly how far we can
        safely move, or we decide we can't move."""
        unaltered = True
        self.rect[index] += offset[index]
        while pg.sprite.spritecollideany(self,obstacles):
            self.rect[index] += (1 if offset[index]<0 else -1)
            unaltered = False
        return unaltered

    def check_keys(self,keys):
        """Find the player's self.x_vel based on currently held keys."""
        self.x_vel = 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.x_vel -= self.speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.x_vel += self.speed

    def check_above(self,obstacles):
        """When jumping, don't enter fall state if there is no room to jump."""
        self.rect.move_ip(0,-1)
        collide = pg.sprite.spritecollideany(self,obstacles)
        self.rect.move_ip(0,1)
        return collide

    def jump(self,obstacles):
        """Called when the user presses the jump button."""
        if not self.fall and not self.check_above(obstacles):
            self.y_vel = self.jump_power
            self.fall = True
            self.on_moving = False

    def update(self,obstacles,keys):
        """Everything we need to stay updated."""
        self.check_keys(keys)
        self.get_position(obstacles)
        self.physics_update()

    def draw(self,surface):
        """Blit the player to the target surface."""
        surface.blit(self.image,self.rect)


class Block(pg.sprite.Sprite):
    """Class representing obstacles."""
    def __init__(self,color,rect):
        pg.sprite.Sprite.__init__(self)
        self.rect = pg.Rect(rect)
        self.image = pg.Surface(self.rect.size).convert()
        self.image.fill(color)
        self.type = "normal"

    def update(self,*args):
        """Overloaded in MovingBlock."""
        pass


class MovingBlock(Block):
    """A class to represent simple moving blocks. Currently only vertical
    and horizontal movement supported."""
    def __init__(self,color,rect,end,axis,delay=500,speed=2):
        Block.__init__(self,color,rect)
        self.start = self.rect.topleft[axis]
        self.axis = axis
        self.end = end
        self.timer = 0.0
        self.delay = delay
        self.speed = speed
        self.waiting = False
        self.type = "moving"

    def update(self,player,obstacles):
        """Update the position of the moving platform. This should be done
        before moving any actors."""
        obstacles = obstacles.copy()
        obstacles.remove(self)
        now = pg.time.get_ticks()
        if not self.waiting:
            if not (self.start <= self.rect[self.axis] <= self.end):
                self.change_direction(now)
            self.rect[self.axis] += self.speed
            self.move_player(now,player,obstacles)
        elif now-self.timer > self.delay:
            self.waiting = False

    def move_player(self,now,player,obstacles):
        """Moves the player both when on top of, or bumped by the platform.
        Collision checks are in place to prevent the block pushing the player
        through a wall."""
        if player.on_moving is self or pg.sprite.collide_rect(self,player):
            axis = self.axis
            offset = (self.speed,self.speed)
            player.check_collisions(offset,axis,obstacles)
            if pg.sprite.collide_rect(self,player):
                if self.speed > 0:
                    self.rect[axis] = player.rect[axis]-self.rect.size[axis]
                else:
                    self.rect[axis] = player.rect[axis]+player.rect.size[axis]
                self.change_direction(now)

    def change_direction(self,now):
        """Called when platform reaches an endpoint or has no more room."""
        self.waiting = True
        self.timer = now
        self.speed *= -1


class Control(object):
    """Class for managing event loop and game states."""
    def __init__(self):
        """Nothing to see here folks.  Move along."""
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.keys = pg.key.get_pressed()
        self.done = False
        self.player = Player((50,875), 4)
        self.viewport = self.screen.get_rect()
        self.level = pg.Surface((1000,1000)).convert()
        self.level_rect = self.level.get_rect()
        self.win_text,self.win_rect = self.make_text()
        self.obstacles = self.make_obstacles()

    def make_text(self):
        """Nothing to see here."""
        font = pg.font.Font(None,100)
        message = "You win. Celebrate."
        text = font.render(message,True,(100,100,175))
        rect = text.get_rect(centerx=self.level_rect.centerx,y=100)
        return text,rect

    def make_obstacles(self):
        """Just adds some arbitrarily placed obstacles to a sprite.Group."""
        obstacles = [Block(pg.Color("chocolate"),(0,980,1000,20)),
                     Block(pg.Color("chocolate"),(0,0,20,1000)),
                     Block(pg.Color("chocolate"),(980,0,20,1000)),
                     Block(pg.Color("darkgreen"),(250,780,200,100)),
                     Block(pg.Color("darkgreen"),(600,880,200,100)),
                     Block(pg.Color("darkgreen"),(20,360,880,40)),
                     Block(pg.Color("darkgreen"),(20,630,50,20)),
                     Block(pg.Color("darkgreen"),(80,530,50,20)),
                     Block(pg.Color("darkgreen"),(130,470,200,215)),
                     Block(pg.Color("darkgreen"),(20,760,30,20)),
                     Block(pg.Color("darkgreen"),(400,740,30,40)),
                     MovingBlock(pg.Color("olivedrab"),(20,740,75,20),325,0),
                     MovingBlock(pg.Color("olivedrab"),(600,500,100,20),880,0)]
        rect = pg.Rect(420,475,100,20)
        fast = MovingBlock(pg.Color("olivedrab"),rect,550,1,speed=3,delay=200)
        obstacles.append(fast)
        return pg.sprite.Group(obstacles)

    def update_viewport(self):
        """The viewport will stay centered on the player unless the player
        approaches the edge of the map."""
        for i in (0,1):
            minimal = max(0,self.player.rect.center[i]-self.viewport.size[i]//2)
            maximal = self.level_rect.size[i]-self.viewport.size[i]
            self.viewport[i] = min(minimal,maximal)

    def event_loop(self):
        """We can always quit, and the player can sometimes jump."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump(self.obstacles)

    def update(self):
        """Update the player, object, and redraw screen."""
        self.player.check_moving(self.obstacles)
        self.obstacles.update(self.player,self.obstacles)
        self.player.update(self.obstacles,self.keys)
        self.update_viewport()
        self.level.fill(pg.Color("lightblue"))
        self.obstacles.draw(self.level)
        self.level.blit(self.win_text,self.win_rect)
        self.player.draw(self.level)
        self.screen.blit(self.level,(0,0),self.viewport)

    def main_loop(self):
        """As simple as it gets."""
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)
            caption = "{} - FPS: {:.2f}".format(CAPTION,self.clock.get_fps())
            pg.display.set_caption(caption)


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode((700,500))
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
