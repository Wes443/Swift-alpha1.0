import pygame
import random
from data.constants import *
vec = pygame.math.Vector2

class Cursor(pygame.sprite.Sprite):
    def __init__(self, game):
        self._layer = LAYER_2
        self.groups = game.cursor_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.cursor
        self.rect = self.image.get_rect()

    def update(self):
        pygame.mouse.set_visible(False)
        self.rect.x, self.rect.y = pygame.mouse.get_pos()

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = LAYER_1
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.right_ball_cycle[0]
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = (y * TILE_SIZE)

        #player settings
        self.ball_speed = 6

        #counter variables
        self.current_frame = 0
        self.idle_counter = 0

        # lower number means LONGER duration (vise-versa)
        self.boost_duration = 5
        self.slow_duration = 3

        #boolean variables
        self.spawn = True

        self.is_boosting = False
        self.is_slowing = False
        self.slow_for_demo = False

        self.facing_left = False
        self.facing_right = True

        self.going_up = False
        self.going_left = False
        self.going_down = False
        self.going_right = False

        #string variables
        self.sequence = ""

    def update(self):

        if self.is_boosting:
            self.game.boost += self.boost_duration
            self.ball_speed = 10

            if self.game.boost > WIDTH:
                self.is_boosting = False
                self.game.recharge_boost = True

        elif self.is_slowing:
            self.game.slow += self.slow_duration
            self.ball_speed = 1

            if self.game.slow > WIDTH:
                self.is_slowing = False
                self.game.recharge_slow = True

        elif self.slow_for_demo:
            self.ball_speed = 1

        else:
            self.ball_speed = 6

        if self.game.recharge_boost:
            self.game.boost -= self.boost_duration

            if self.game.boost < (WIDTH - 80):
                self.game.boost = (WIDTH - 80)
                self.game.recharge_boost = False

        if self.game.recharge_slow:
            self.game.slow -= self.slow_duration

            if self.game.slow < (WIDTH - 80):
                self.game.slow = (WIDTH - 80)
                self.game.recharge_slow = False


        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_w] and not self.spawn:
            if self.going_down:
                self.game.playing = False
                self.game.reset()

            self.going_up = True
            self.going_left = False
            self.going_down = False
            self.going_right = False

        elif keystate[pygame.K_a] and not self.spawn:
            if self.going_right:
                self.game.playing = False
                self.game.reset()

            self.facing_right = False
            self.facing_left = True

            self.going_up = False
            self.going_left = True
            self.going_down = False
            self.going_right = False

        elif keystate[pygame.K_s] and not self.spawn:
            if self.going_up:
                self.game.playing = False
                self.game.reset()

            self.going_up = False
            self.going_left = False
            self.going_down = True
            self.going_right = False

        elif keystate[pygame.K_d]:
            if self.going_left:
                self.game.playing = False
                self.game.reset()

            self.spawn = False
            self.facing_right = True
            self.facing_left = False

            self.going_up = False
            self.going_left = False
            self.going_down = False
            self.going_right = True

        #ball animation
        if self.going_right:
            self.rect.x += self.ball_speed

            self.current_frame += FRAME_RATE
            if self.current_frame >= len(self.game.right_ball_cycle):
                self.current_frame = 0

            self.image = self.game.right_ball_cycle[int(self.current_frame)]

        if self.going_left:
            self.rect.x -= self.ball_speed

            self.current_frame += FRAME_RATE
            if self.current_frame >= len(self.game.left_ball_cycle):
                self.current_frame = 0

            self.image = self.game.left_ball_cycle[int(self.current_frame)]

        if self.going_up:
            self.rect.y -= self.ball_speed

            if self.facing_right:
                self.current_frame += FRAME_RATE
                if self.current_frame >= len(self.game.right_ball_cycle):
                    self.current_frame = 0

                self.image = self.game.right_ball_cycle[int(self.current_frame)]

            if self.facing_left:
                self.current_frame += FRAME_RATE
                if self.current_frame >= len(self.game.left_ball_cycle):
                    self.current_frame = 0

                self.image = self.game.left_ball_cycle[int(self.current_frame)]

        if self.going_down:
            self.rect.y += self.ball_speed

            if self.facing_right:
                self.current_frame += FRAME_RATE
                if self.current_frame >= len(self.game.right_ball_cycle):
                    self.current_frame = 0

                self.image = self.game.right_ball_cycle[int(self.current_frame)]

            if self.facing_left:
                self.current_frame += FRAME_RATE
                if self.current_frame >= len(self.game.left_ball_cycle):
                    self.current_frame = 0

                self.image = self.game.left_ball_cycle[int(self.current_frame)]

class DemoPlayer(pygame.sprite.Sprite):
    def __init__(self, game, x, y, location):
        self._layer = LAYER_2
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.location = location

        if (self.location == "title_screen"):
            self.image = self.game.player_jump_R
            self.rect = self.image.get_rect()

        if (self.location == "end_cutscene"):
            self.image = self.game.right_ball_cycle[0]
            self.player_img = self.game.player_jump_R
            self.rect = self.player_img.get_rect()

        if (self.location == "intro_cutscene"):
            self.image = self.game.player_jump_R
            self.rect = self.image.get_rect()

        self.facing_R = True
        self.facing_L = False
        self.walking_R = False
        self.walking_L = False
        self.idle_R = False
        self.idle_L = False

        self.walk_counter = 0
        self.idle_counter = 0

        self.default_x = x * TILE_SIZE
        self.default_y = y * TILE_SIZE

        self.human_frame_counter = 0
        self.ball_frame_counter = 0

        self.detect_collision = True
        self.counting = False
        self.counter = 0

        if (self.location == "title_screen"):
            self.human_form = True
            self.ball_form = False

        if (self.location == "end_cutscene"):
            self.human_form = False
            self.ball_form = True

        if (self.location == "intro_cutscene"):
            self.human_form = True
            self.ball_form = False

        self.pos = vec(x, y) * TILE_SIZE
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def movement(self):

        if self.pos.y > HEIGHT:
            self.kill()
            self.human_frame_counter = 0
            self.game.game_over = True

        if (self.location == "title_screen"):

            self.acc = vec(0, PLAYER_GRAVITY)

            self.human_frame_counter += 1

            if self.human_frame_counter > 250:
                self.acc.x = PLAYER_ACC
                self.walking_R = True
                self.walking_L = False
                self.idle_R = False
                self.idle_L = False

        if (self.location == "intro_cutscene"):
            self.acc = vec(0, PLAYER_SLOW_GRAVITY)

            self.human_frame_counter += 1

            if self.human_frame_counter > 500 and self.human_frame_counter < 1050:
                self.acc.x = PLAYER_SLOWEST_ACC
                self.walking_R = True
                self.idle_R = False

            if self.human_frame_counter > 1050 and self.human_frame_counter < 1600:
                self.acc.x = 0
                self.walking_R = False
                self.idle_R = True

            if self.human_frame_counter > 1600 and self.human_frame_counter < 1700:
                self.acc.x = PLAYER_SLOWEST_ACC
                self.walking_R = True
                self.idle_R = False

            if self.human_frame_counter > 1700:
                self.human_frame_counter = 0
                self.game.cutscene_loop_2 = False

        if (self.location == "end_cutscene" and self.human_form):
            self.acc = vec(0, PLAYER_GRAVITY)

            self.human_frame_counter += 1
            self.image = self.game.player_jump_R

            if self.human_frame_counter > 200 and self.human_frame_counter < 700:
                self.acc.x = PLAYER_SLOW_ACC
                self.walking_R = True
                self.idle_R = False

            if self.human_frame_counter > 700 and self.human_frame_counter < 875:
                self.acc.x = 0
                self.walking_R = False
                self.idle_R = True

            if self.human_frame_counter > 875 and self.human_frame_counter < 943:
                self.acc.x = PLAYER_SLOW_ACC
                self.walking_R = True
                self.idle_R = False

        if self.human_form:

            self.acc.x += self.vel.x * PLAYER_FRICTION
            self.vel += self.acc
            self.pos += self.vel + 0.5 * self.acc

            # player idle animation
            if self.idle_R:
                self.walking_R = False
                self.image = self.game.player_idle_1_R

                self.idle_counter += IDLE_RATE

                if self.idle_counter > 2:
                    self.image = self.game.player_idle_2_R

                    if self.idle_counter > 3:
                        self.image = self.game.player_idle_1_R
                        self.idle_counter = 0

            if self.idle_L:
                self.walking_L = False
                self.image = self.game.player_idle_1_L

                self.idle_counter += IDLE_RATE

                if self.idle_counter > 2:
                    self.image = self.game.player_idle_2_L

                    if self.idle_counter > 3:
                        self.image = self.game.player_idle_1_L
                        self.idle_counter = 0

            # player walking animation
            if self.walking_R:
                self.facing_R = True
                self.facing_L = False
                self.walk_counter += WALK_RATE

                if self.walk_counter >= len(self.game.walkcycle_R):
                    self.walk_counter = 0

                self.image = self.game.walkcycle_R[int(self.walk_counter)]

            if self.walking_L:
                self.facing_R = False
                self.facing_L = True
                self.walk_counter += WALK_RATE

                if self.walk_counter >= len(self.game.walkcycle_L):
                    self.walk_counter = 0

                self.image = self.game.walkcycle_L[int(self.walk_counter)]

        if self.ball_form and self.location == "title_screen":
            self.pos.x += 4
            self.ball_frame_counter += FRAME_RATE

            if self.ball_frame_counter >= len(self.game.right_ball_cycle):
                self.ball_frame_counter = 0

            self.image = self.game.right_ball_cycle[int(self.ball_frame_counter)]

            if self.pos.x > WIDTH:
                self.pos.x = self.default_x
                self.pos.y = self.default_y
                self.image = self.game.player_jump_R
                self.human_form = True
                self.ball_form = False

        if self.ball_form and self.location == "end_cutscene":
            self.pos.x += 5
            self.ball_frame_counter += FRAME_RATE

            if self.ball_frame_counter >= len(self.game.right_ball_cycle):
                self.ball_frame_counter = 0

            self.image = self.game.right_ball_cycle[int(self.ball_frame_counter)]

    def collide_with_walls(self):
        hits = pygame.sprite.spritecollide(self, self.game.tile_set, False)
        if hits:
            if self.vel.y > 0: # if player is going down
                self.pos.y = hits[0].rect.top - self.rect.height

                if self.facing_R:
                    self.idle_R = True

                if self.facing_L:
                    self.idle_L = True

            if self.vel.y < 0: # if player is going up
                self.pos.y = hits[0].rect.bottom

            self.rect.y = self.pos.y
            self.vel.y = 0

    def collide_with_portal(self):

        if self.location == "title_screen":
            hits = pygame.sprite.spritecollide(self, self.game.demo_portal, False)
            if hits:
                self.human_form = False
                self.ball_form = True
                self.human_frame_counter = 0
                self.walking_R = False

        if self.location == "end_cutscene":
            if self.detect_collision:
                hits = pygame.sprite.spritecollide(self, self.game.demo_portal, False)
                if hits:
                    self.counting = True
                    self.detect_collision = False

        if self.counting:
            self.counter += 1
            if self.counter > 40:
                self.counting = False
                self.counter = 0
                self.human_form = True
                self.ball_form = False

    def update(self):
        self.movement()
        self.collide_with_portal()
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        self.collide_with_walls()

class TileSet(pygame.sprite.Sprite):
    def __init__(self, game, x, y, variant):
        self._layer = LAYER_0
        if (variant == "r" or variant == "s" or variant == "t" or variant == "i"):
            self.groups = game.all_sprites
        else:
            self.groups = game.all_sprites, game.tile_set

        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rand_num = random.randint(1, 2)

        if variant == 1:
            if self.rand_num == 1:
                self.image = self.game.floor
            else:
                self.image = self.game.floor_variant

        if variant == 2:
            if self.rand_num == 1:
                self.image = self.game.ceil
            else:
                self.image = self.game.ceil_variant

        if variant == 3:
            if self.rand_num == 1:
                self.image = self.game.right_wall
            else:
                self.image = self.game.right_wall_variant

        if variant == 4:
            if self.rand_num == 1:
                self.image = self.game.left_wall
            else:
                self.image = self.game.left_wall_variant

        if variant == 5:
            self.image = self.game.TR_outside_corner

        if variant == 6:
            self.image = self.game.TL_outside_corner

        if variant == 7:
            self.image = self.game.BR_outside_corner

        if variant == 8:
            self.image = self.game.BL_outside_corner

        if variant == 9:
            self.image = self.game.TR_inside_corner

        if variant == "a":
            self.image = self.game.TL_inside_corner

        if variant == "b":
            self.image = self.game.BR_inside_corner

        if variant == "c":
            self.image = self.game.BL_inside_corner

        if variant == "d":
            self.image = self.game.double_inside_corner_left

        if variant == "e":
            self.image = self.game.double_inside_corner_right

        if variant == "f":
            self.image = self.game.corner_triple_left

        if variant == "g":
            self.image = self.game.corner_triple_right

        if variant == "h":
            if self.rand_num == 1:
                self.image = self.game.floor_and_ceil
            else:
                self.image = self.game.floor_and_ceil_variant

        if variant == "i":
            if self.rand_num == 1:
                self.image = self.game.bkgd_greebling
            else:
                self.image = self.game.bkgd_greebling_variant

        #skip variant == "j" through variant == "q"

        if variant == "r":
            if self.rand_num == 1:
                self.image = self.game.greebling_high
            else:
                self.image = self.game.greebling_high_variant

        if variant == "s":
            if self.rand_num == 1:
                self.image = self.game.greebling_low
            else:
                self.image = self.game.greebling_low_variant

        if variant == "t":
            if self.rand_num == 1:
                self.image = self.game.greebling
            else:
                self.image = self.game.greebling_variant

        if variant == "u":
            self.image = self.game.floor_and_TL_corner

        if variant == "v":
            self.image = self.game.floor_and_TR_corner

        if variant == "w":
            self.image = self.game.ceil_and_BL_corner

        if variant == "x":
            self.image = self.game.ceil_and_BR_corner

        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class WallLaser(pygame.sprite.Sprite):
    def __init__(self, game, x, y, state):
        self._layer = LAYER_1
        self.groups = game.all_sprites, game.lasers
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        if state == "right":
            self.image = self.game.right_wall_laser
            self.rect = self.image.get_rect()
            self.rect.x = (x * TILE_SIZE) + 56
            self.rect.y = y * TILE_SIZE

        if state == "left":
            self.image = self.game.left_wall_laser
            self.rect = self.image.get_rect()
            self.rect.x = x * TILE_SIZE
            self.rect.y = y * TILE_SIZE

        if state == "floor":
            self.image = self.game.floor_wall_laser
            self.rect = self.image.get_rect()
            self.rect.x = x * TILE_SIZE
            self.rect.y = (y * TILE_SIZE) + 56

        if state == "ceil":
            self.image = self.game.ceil_wall_laser
            self.rect = self.image.get_rect()
            self.rect.x = x * TILE_SIZE
            self.rect.y = y * TILE_SIZE

class LaserRock(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = LAYER_1
        self.groups = game.all_sprites, game.lasers
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.red_laser_rock
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

        self.initial_x = x * TILE_SIZE
        self.initial_y = y * TILE_SIZE

        #varibles
        self.down = True
        self.up = False

        self.counter = False
        self.count = 0
        self.wait_limit = 80

    def update(self):

        keystate = pygame.key.get_pressed()

        if self.down:
            self.rect.y += 5

            if self.rect.y > (self.initial_y + (2 * TILE_SIZE)):
                self.down = False
                self.up = True

        if self.up:
            self.rect.y -= 1

            if self.rect.y < self.initial_y:
                self.rect.y = self.initial_y
                self.counter = True
                self.up = False

        if self.counter:
            self.count += 1

            if self.count > self.wait_limit:
                self.counter = False
                self.count = 0
                self.down = True

class Lasers(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        self._layer = LAYER_2
        self.groups = game.all_sprites, game.lasers
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.direction = direction
        self.reaction_limit = 150

        if self.direction == "right":
            self.image = self.game.right_red_laser
            self.min_x = (x * TILE_SIZE) - self.reaction_limit
            self.max_x = (x * TILE_SIZE)
            self.min_y = (y * TILE_SIZE)
            self.max_y = (y * TILE_SIZE) + self.image.get_height()

        if self.direction == "left":
            self.image = self.game.left_red_laser
            self.max_x = (x * TILE_SIZE) + self.reaction_limit
            self.min_x = (x * TILE_SIZE)
            self.min_y = (y * TILE_SIZE)
            self.max_y = (y * TILE_SIZE) + self.image.get_height()

        if self.direction == "down":
            self.image = self.game.down_red_laser
            self.min_x = (x * TILE_SIZE)
            self.max_x = (x * TILE_SIZE) + self.image.get_width()
            self.max_y = (y * TILE_SIZE)
            self.min_y = (y * TILE_SIZE) - self.reaction_limit

        if self.direction == "up":
            self.image = self.game.up_red_laser
            self.min_x = (x * TILE_SIZE)
            self.max_x = (x * TILE_SIZE) + self.image.get_width()
            self.max_y = (y * TILE_SIZE) + self.reaction_limit
            self.min_y = (y * TILE_SIZE)

        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

    def update(self):
        keystate = pygame.key.get_pressed()

        if self.direction == "right":
            if self.game.player.rect.x > self.min_x and self.game.player.rect.x < self.max_x and self.game.player.rect.y > self.min_y and self.game.player.rect.y < self.max_y:
                self.image = self.game.right_green_laser
                if keystate[pygame.K_SPACE]:
                    self.kill()

        if self.direction == "left":
            if self.game.player.rect.x > self.min_x and self.game.player.rect.x < self.max_x and self.game.player.rect.y > self.min_y and self.game.player.rect.y < self.max_y:
                self.image = self.game.left_green_laser
                if keystate[pygame.K_SPACE]:
                    self.kill()

        if self.direction == "down":
            if self.game.player.rect.x > self.min_x and self.game.player.rect.x < self.max_x and self.game.player.rect.y > self.min_y and self.game.player.rect.y < self.max_y:
                self.image = self.game.down_green_laser
                if keystate[pygame.K_SPACE]:
                    self.kill()

        if self.direction == "up":
            if self.game.player.rect.x > self.min_x and self.game.player.rect.x < self.max_x and self.game.player.rect.y > self.min_y and self.game.player.rect.y < self.max_y:
                self.image = self.game.up_green_laser
                if keystate[pygame.K_SPACE]:
                    self.kill()

class PuzzleLaser(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        self._layer = LAYER_2
        self.groups = game.all_sprites, game.lasers
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        if direction == "right":
            self.image = self.game.right_red_laser

        if direction == "left":
            self.image = self.game.left_red_laser

        if direction == "down":
            self.image = self.game.down_red_laser

        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

    def update(self):
        if self.game.solved:
            self.kill()

class InvisibleBlock(pygame.sprite.Sprite):
    def __init__(self, game, x, y, order):
        self._layer = LAYER_0
        self.order = order
        if self.order == "1":
            self.groups = game.invis_block_1, game.all_sprites

        if self.order == "2":
            self.groups = game.invis_block_2, game.all_sprites

        if self.order == "3":
            self.groups = game.invis_block_3, game.all_sprites

        if  self.order == "4":
            self.groups = game.invis_block_4, game.all_sprites

        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((64, 64))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class StartPortal(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = LAYER_1
        self.groups = game.all_sprites, game.lasers
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.start_portal
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class EndPortal(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = LAYER_1
        self.groups = game.all_sprites, game.portals
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        if self.game.current_level == "tut" or self.game.current_level == "5" or self.game.current_level == "6" or self.game.current_level == "10":
            self.image = self.game.right_end_portal

        else:
            self.image = self.game.left_end_portal

        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class DemoPortal(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = LAYER_1
        self.groups = game.all_sprites, game.demo_portal
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.start_portal_right
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = (y * TILE_SIZE) + 20

class PlayButton(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = LAYER_1
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.play_button

        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

    def update(self):
        self.pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(self.pos):
            self.image = self.game.play_button_hover
            if pygame.mouse.get_pressed()[0] == 1:
                self.game.title_screen_loop = False
                self.game.intro_cutscene()

        else:
            self.image = self.game.play_button

class TitleScreenButton(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.button
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.title_screen_button

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(self.pos):
            self.image = self.game.title_screen_button_hover
            if pygame.mouse.get_pressed()[0] == 1:
                self.game.cutscene_loop_1 = False
                self.game.title_screen()

        else:
            self.image = self.game.title_screen_button

class ExitButton(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = LAYER_1
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.exit_button

        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

    def update(self):
        self.pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(self.pos):
            self.image = self.game.exit_button_hover
            if pygame.mouse.get_pressed()[0] == 1:
                self.game.title_screen_loop = False
                self.game.running = False

        else:
            self.image = self.game.exit_button

class TutorialSigns(pygame.sprite.Sprite):
    def __init__(self, game, x, y, type):
        self._layer = LAYER_1
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = type

        if self.type == "arrowkeys":
            self.image = self.game.arrow_keys[0]

        if self.type == "laser_tut":
            self.image = self.game.laser_tut[0]

        if self.type == "meters":
            self.image = self.game.meters_tut[0]

        if self.type == "hint1":
            self.image = self.game.hint_1

        if self.type == "hint2":
            self.image = self.game.hint_2

        if self.type == "hint3":
            self.image = self.game.hint_3

        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

        self.counter = 0

    def update(self):

        if self.type == "arrowkeys":
            self.counter += 0.025

            if self.counter >= len(self.game.arrow_keys):
                self.counter = 0

            self.image = self.game.arrow_keys[int(self.counter)]

        if self.type == "meters":
            self.counter += 0.025

            if self.counter >= len(self.game.meters_tut):
                self.counter = 0

            self.image = self.game.meters_tut[int(self.counter)]

        if self.type == "laser_tut":
            self.max_x = self.rect.x + 60
            self.min_x = self.rect.x - 200

            if self.game.player.rect.x > self.min_x and self.game.player.rect.x < self.max_x:
                self.game.player.slow_for_demo = True
            else:
                self.game.player.slow_for_demo = False

            self.counter += 0.1

            if self.counter >= len(self.game.laser_tut):
                self.counter = 0

            self.image = self.game.laser_tut[int(self.counter)]

class LevelSigns(pygame.sprite.Sprite):
    def __init__(self, game, x, y, level):
        self._layer = LAYER_1
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        if level == "tut":
            self.image = self.game.tutorial_sign

        if level == "1":
            self.image = self.game.level_signs[0]

        if level == "2":
            self.image = self.game.level_signs[1]

        if level == "3":
            self.image = self.game.level_signs[2]

        if level == "4":
            self.image = self.game.level_signs[3]

        if level == "5":
            self.image = self.game.level_signs[4]

        if level == "6":
            self.image = self.game.level_signs[5]

        if level == "7":
            self.image = self.game.level_signs[6]

        if level == "8":
            self.image = self.game.level_signs[7]

        if level == "9":
            self.image = self.game.level_signs[8]

        if level == "10":
            self.image = self.game.level_signs[9]

        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class Bridge(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = LAYER_1
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.bridge
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

    def update(self):
        if self.game.demo_player.human_frame_counter > 1000:
            self.image = self.game.bridge_broken

class InvisibleBridge(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = LAYER_0
        self.groups = game.all_sprites, game.tile_set
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((128, 32))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

    def update(self):
        if self.game.demo_player.human_frame_counter > 1000:
            self.kill()
