import pygame, sys
from data.constants import *
from data.sprites import *
from data.tools import *

#custom font
def clip(surf,x,y,x_size,y_size):
    handle_surf = surf.copy()
    clipR = pygame.Rect(x,y,x_size,y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()

class Font():

    def __init__(self):

        self.img_dir = "data/img/"
        #self.img_dir = "Swift_Alpha_1.0/data/img/"

        self.spacing = 1
        self.character_order = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','.','-',',',':','+','\'','!','?','0','1','2','3','4','5','6','7','8','9']
        font_img = pygame.image.load(self.img_dir + "text_strip.png").convert()
        font_img.set_colorkey(BLACK)
        current_char_width = 0
        self.characters = {}
        character_count = 0
        for x in range(font_img.get_width()):
            c = font_img.get_at((x, 0))
            if c[0] == 127:
                char_img = clip(font_img, x - current_char_width, 0, current_char_width, font_img.get_height())
                self.characters[self.character_order[character_count]] = char_img.copy()
                character_count += 1
                current_char_width = 0
            else:
                current_char_width += 1
        self.space_width = self.characters['A'].get_width()

    def render(self, surf, text, loc):
        x_offset = 0
        for char in text:
            if char != ' ':
                surf.blit(self.characters[char], (loc[0] + x_offset, loc[1]))
                x_offset += self.characters[char].get_width() + self.spacing
            else:
                x_offset += self.space_width + self.spacing

#main game class
class Game():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_level = "tut"

        #variables for the boost/slow meter
        self.boost = WIDTH - 80
        self.slow = WIDTH - 80

        self.recharge_boost = False
        self.recharge_slow = False

        #variables for detecting bugs
        self.space_holding = False
        self.space_hold_counter = 0

        self.counter = 0
        self.counting = True

        #variable for the moving text (in the tut lvl)
        self.initial_y = (HEIGHT - 85)

        #boolean variables for the puzzle
        self.collide_1 = True
        self.collide_2 = True
        self.collide_3 = True
        self.collide_4 = True
        self.solved = False

        self.load_assets()
        self.map_data()

    #variables that neeed to be reset (after every death)
    def reset(self):
        self.boost = WIDTH - 80
        self.slow = WIDTH - 80
        self.space_holding = False
        self.space_hold_counter = 0
        self.initial_y = (HEIGHT - 85)
        self.counter = 0
        self.collide_1 = True
        self.collide_2 = True
        self.collide_3 = True
        self.collide_4 = True
        self.solved = False

    #loading all the images for the game
    def load_assets(self):
        #file directories
        self.img_dir = "data/img/"
        # self.img_dir = "Swift_Alpha_1.0/data/img/"

        self.map_dir = "data/maps/"
        # self.map_dir = "Swift_Alpha_1.0/data/maps/"

        #player (main form) sprites
        self.right_ball_cycle = []
        self.left_ball_cycle = []

        for frame in range(0, 6):
            filename = "ball_{}.png".format(frame)
            img = pygame.transform.scale(pygame.image.load(self.img_dir + filename), (64, 64)).convert()
            img.set_colorkey(BLACK)
            self.right_ball_cycle.append(img)

        for frame in range(0, 6):
            filename = "ball_{}.png".format(frame)
            img_scaled = pygame.transform.scale(pygame.image.load(self.img_dir + filename), (64, 64)).convert()
            img_scaled.set_colorkey(BLACK)
            img_flipped = pygame.transform.flip(img_scaled, True, False)
            self.left_ball_cycle.append(img_flipped)

        #player idle sprites
        player_idle_1 = pygame.image.load(self.img_dir + "idle_1.png").convert()
        player_idle_2 = pygame.image.load(self.img_dir + "idle_2.png").convert()

        self.player_idle_1_R = pygame.transform.scale(player_idle_1, (80, 80))
        self.player_idle_1_R.set_colorkey(BLACK)

        self.player_idle_2_R = pygame.transform.scale(player_idle_2, (80, 80))
        self.player_idle_2_R.set_colorkey(BLACK)

        self.player_idle_1_L = pygame.transform.flip(self.player_idle_1_R, True, False)
        self.player_idle_1_L.set_colorkey(BLACK)

        self.player_idle_2_L = pygame.transform.flip(self.player_idle_2_R, True, False)
        self.player_idle_2_L.set_colorkey(BLACK)

        #player jumping sprite
        player_jump = pygame.image.load(self.img_dir + "jump.png").convert()
        self.player_jump_R = pygame.transform.scale(player_jump, (80, 80))
        self.player_jump_R.set_colorkey(BLACK)
        self.player_jump_L = pygame.transform.flip(self.player_jump_R, True, False)
        self.player_jump_L.set_colorkey(BLACK)

        #player walking sprites
        self.walkcycle_R = []
        self.walkcycle_L = []

        for frame in range(1, 9):
            filename = "wc_{}.png".format(frame)
            img = pygame.transform.scale(pygame.image.load(self.img_dir + filename), (80, 80)).convert()
            img.set_colorkey(BLACK)
            self.walkcycle_R.append(img)

        for frame in range(1, 9):
            filename = "wc_{}.png".format(frame)
            img_scaled = pygame.transform.scale(pygame.image.load(self.img_dir + filename), (80, 80)).convert()
            img_scaled.set_colorkey(BLACK)
            img_flipped = pygame.transform.flip(img_scaled, True, False)
            self.walkcycle_L.append(img_flipped)

        #tileset

        #walls
        floor = pygame.image.load(self.img_dir + "floor.png").convert()
        self.floor = pygame.transform.scale(floor, (64, 64))
        self.floor.set_colorkey(BLACK)

        floor_variant = pygame.image.load(self.img_dir + "floor_variant.png").convert()
        self.floor_variant = pygame.transform.scale(floor_variant, (64, 64))
        self.floor_variant.set_colorkey(BLACK)

        self.ceil = pygame.transform.flip(self.floor, False, True)
        self.ceil_variant = pygame.transform.flip(self.floor_variant, False, True)

        self.right_wall = pygame.transform.rotate(self.floor, 90)
        self.right_wall_variant = pygame.transform.rotate(self.floor_variant, 90)

        self.left_wall = pygame.transform.rotate(self.floor, -90)
        self.left_wall_variant = pygame.transform.rotate(self.floor_variant, -90)

        #outside corners
        TR_outside_corner = pygame.image.load(self.img_dir + "outside_corner.png").convert()
        self.TR_outside_corner = pygame.transform.scale(TR_outside_corner, (64, 64))
        self.TR_outside_corner.set_colorkey(BLACK)
        self.TL_outside_corner = pygame.transform.flip(self.TR_outside_corner, True, False)
        self.BR_outside_corner = pygame.transform.flip(self.TR_outside_corner, False, True)
        self.BL_outside_corner = pygame.transform.flip(self.BR_outside_corner, True, False)

        #inside corners
        BL_inside_corner = pygame.image.load(self.img_dir + "inside_corner.png").convert()
        self.BL_inside_corner = pygame.transform.scale(BL_inside_corner, (64, 64))
        self.BL_inside_corner.set_colorkey(BLACK)
        self.BR_inside_corner = pygame.transform.flip(self.BL_inside_corner, True, False)
        self.TL_inside_corner = pygame.transform.flip(self.BL_inside_corner, False, True)
        self.TR_inside_corner = pygame.transform.flip(self.TL_inside_corner, True, False)

        #double inside corners
        double_inside_corner_left = pygame.image.load(self.img_dir + "double_inside_corner.png").convert()
        self.double_inside_corner_left = pygame.transform.scale(double_inside_corner_left, (64, 64))
        self.double_inside_corner_left.set_colorkey(BLACK)
        self.double_inside_corner_right = pygame.transform.flip(self.double_inside_corner_left, True, False)

        #floor and inside corners
        floor_and_TL_corner = pygame.image.load(self.img_dir + "floor_and_corner.png").convert()
        self.floor_and_TL_corner = pygame.transform.scale(floor_and_TL_corner, (64, 64))
        self.floor_and_TL_corner.set_colorkey(BLACK)
        self.floor_and_TR_corner = pygame.transform.flip(self.floor_and_TL_corner, True, False)
        self.ceil_and_BL_corner = pygame.transform.flip(self.floor_and_TL_corner, False, True)
        self.ceil_and_BR_corner = pygame.transform.flip(self.ceil_and_BL_corner, True, False)

        #floor and ceiling
        floor_and_ceil = pygame.image.load(self.img_dir + "floor_and_ceil.png").convert()
        self.floor_and_ceil = pygame.transform.scale(floor_and_ceil, (64, 64))
        self.floor_and_ceil.set_colorkey(BLACK)

        floor_and_ceil_variant = pygame.image.load(self.img_dir + "floor_and_ceil_variant.png").convert()
        self.floor_and_ceil_variant = pygame.transform.scale(floor_and_ceil_variant, (64, 64))
        self.floor_and_ceil_variant.set_colorkey(BLACK)

        #triple corners
        corner_triple_left = pygame.image.load(self.img_dir + "corner_triple.png").convert()
        self.corner_triple_left = pygame.transform.scale(corner_triple_left, (64, 64))
        self.corner_triple_left.set_colorkey(BLACK)
        self.corner_triple_right = pygame.transform.flip(self.corner_triple_left, True, False)

        #greebling
        greebling = pygame.image.load(self.img_dir + "greebling.png").convert()
        self.greebling = pygame.transform.scale(greebling, (64, 64))
        self.greebling.set_colorkey(BLACK)

        greebling_variant = pygame.image.load(self.img_dir + "greebling_variant.png").convert()
        self.greebling_variant = pygame.transform.scale(greebling_variant, (64, 64))
        self.greebling_variant.set_colorkey(BLACK)

        greebling_high = pygame.image.load(self.img_dir + "greebling_thin.png").convert()
        self.greebling_high = pygame.transform.scale(greebling_high, (64, 64))
        self.greebling_high.set_colorkey(BLACK)

        greebling_high_variant = pygame.image.load(self.img_dir + "greebling_thin_variant.png").convert()
        self.greebling_high_variant = pygame.transform.scale(greebling_high_variant, (64, 64))
        self.greebling_high_variant.set_colorkey(BLACK)

        self.greebling_low = pygame.transform.flip(self.greebling_high, False, True)
        self.greebling_low_variant = pygame.transform.flip(self.greebling_high_variant, False, True)

        #background greebling
        bkgd_greebling = pygame.image.load(self.img_dir + "bkgd_greebling.png").convert()
        self.bkgd_greebling = pygame.transform.scale(bkgd_greebling, (64, 64))
        self.bkgd_greebling.set_colorkey(BLACK)

        bkgd_greebling_variant = pygame.image.load(self.img_dir + "bkgd_greebling_variant.png").convert()
        self.bkgd_greebling_variant = pygame.transform.scale(bkgd_greebling_variant, (64, 64))
        self.bkgd_greebling_variant.set_colorkey(BLACK)

        #obstacles

        #green lasers
        green_laser = pygame.image.load(self.img_dir + "green_laser.png").convert()
        self.right_green_laser = pygame.transform.scale(green_laser, (16, 128))
        self.right_green_laser.set_colorkey(BLACK)
        self.left_green_laser = pygame.transform.flip(self.right_green_laser, True, False)
        self.down_green_laser = pygame.transform.rotate(self.right_green_laser, -90)
        self.up_green_laser = pygame.transform.rotate(self.right_green_laser, 90)

        #red lasers
        red_laser = pygame.image.load(self.img_dir + "red_laser.png").convert()
        self.right_red_laser = pygame.transform.scale(red_laser, (16, 128))
        self.right_red_laser.set_colorkey(BLACK)
        self.left_red_laser = pygame.transform.flip(self.right_red_laser, True, False)
        self.down_red_laser = pygame.transform.rotate(self.right_red_laser, -90)
        self.up_red_laser = pygame.transform.rotate(self.right_red_laser, 90)

        #wall lasers
        wall_laser = pygame.image.load(self.img_dir + "wall_laser.png").convert()
        self.floor_wall_laser = pygame.transform.scale(wall_laser, (64, 8))
        self.floor_wall_laser.set_colorkey(BLACK)
        self.ceil_wall_laser = pygame.transform.flip(self.floor_wall_laser, False, True)
        self.right_wall_laser = pygame.transform.rotate(self.floor_wall_laser, 90)
        self.left_wall_laser = pygame.transform.rotate(self.floor_wall_laser, -90)

        #laser rocks
        red_laser_rock = pygame.image.load(self.img_dir + "laser_rock_red.png").convert()
        self.red_laser_rock = pygame.transform.scale(red_laser_rock, (64, 64))
        self.red_laser_rock.set_colorkey(BLACK)

        green_laser_rock = pygame.image.load(self.img_dir + "laser_rock_green.png").convert()
        self.green_laser_rock = pygame.transform.scale(green_laser_rock, (64, 64))
        self.green_laser_rock.set_colorkey(BLACK)

        #miscellaneous

        #bridge (used in end cutscene)
        bridge = pygame.image.load(self.img_dir + "bridge.png").convert()
        self.bridge = pygame.transform.scale(bridge, (128, 32))
        self.bridge.set_colorkey(BLACK)

        bridge_broken = pygame.image.load(self.img_dir + "bridge_broken.png").convert()
        self.bridge_broken = pygame.transform.scale(bridge_broken, (128, 32))
        self.bridge_broken.set_colorkey(BLACK)

        #boost/slow meter
        boost_meter = pygame.image.load(self.img_dir + "boost_bar.png")
        self.boost_meter = pygame.transform.scale(boost_meter, (128, 64))

        slow_meter = pygame.image.load(self.img_dir + "slow_bar.png")
        self.slow_meter = pygame.transform.scale(slow_meter, (128, 64))

        #portals
        start_portal = pygame.image.load(self.img_dir + "start_portal.png").convert()
        self.start_portal = pygame.transform.flip(pygame.transform.scale(start_portal, (64, 64)), True, False)
        self.start_portal.set_colorkey(BLACK)
        self.start_portal_right = pygame.transform.flip(self.start_portal, True, False)

        end_portal = pygame.image.load(self.img_dir +  "end_portal.png").convert()
        self.right_end_portal = pygame.transform.scale(end_portal, (64, 64))
        self.right_end_portal.set_colorkey(BLACK)
        self.left_end_portal = pygame.transform.flip(self.right_end_portal, True, False)

        #mouse cursor sprite
        cursor = pygame.image.load(self.img_dir + "cursor.png")
        self.cursor = pygame.transform.scale(cursor, (16, 16))

        #game mechanics demonstration
        self.arrow_keys = []

        for frame in range(0, 5):
            filename = "arrowkeys_{}.png".format(frame)
            img = pygame.transform.scale(pygame.image.load(self.img_dir + filename), (192, 128)).convert()
            img.set_colorkey(BLACK)
            self.arrow_keys.append(img)

        self.laser_tut = []

        for frame in range(0, 12):
            filename = "laser_tut_{}.png".format(frame)
            img = pygame.transform.scale(pygame.image.load(self.img_dir + filename), (192, 128)).convert()
            img.set_colorkey(BLACK)
            self.laser_tut.append(img)

        self.meters_tut = []

        for frame in range (0,2):
            filename = "boost_slow_tut_{}.png".format(frame)
            img = pygame.transform.scale(pygame.image.load(self.img_dir + filename), (192, 128)).convert()
            img.set_colorkey(BLACK)
            self.meters_tut.append(img)

        hint_1 = pygame.image.load(self.img_dir + "hint_1.png").convert()
        self.hint_1 = pygame.transform.scale(hint_1, (192, 128))
        self.hint_1.set_colorkey(BLACK)

        hint_2 = pygame.image.load(self.img_dir + "hint_2.png").convert()
        self.hint_2 = pygame.transform.scale(hint_2, (192, 128))
        self.hint_2.set_colorkey(BLACK)

        hint_3 = pygame.image.load(self.img_dir + "hint_3.png").convert()
        self.hint_3 = pygame.transform.scale(hint_3, (192, 128))
        self.hint_3.set_colorkey(BLACK)

        #title scren sprites

        #"you died" text
        death_text = pygame.image.load(self.img_dir + "you_died_text.png").convert()
        self.death_text = pygame.transform.scale(death_text, (512, 128))
        self.death_text.set_colorkey(BLACK)

        #logo sign
        logo = pygame.image.load(self.img_dir + "logo.png").convert()
        self.logo = pygame.transform.scale(logo, (640, 320))
        self.logo.set_colorkey(BLACK)

        #level signs
        tutorial_sign = pygame.image.load(self.img_dir + "tutorial_sign.png").convert()
        self.tutorial_sign = pygame.transform.scale(tutorial_sign, (128, 64))
        self.tutorial_sign.set_colorkey(BLACK)

        self.level_signs = []

        for frame in range(1, 11):
            filename = "lvl_{}_sign.png".format(frame)
            img = pygame.transform.scale(pygame.image.load(self.img_dir + filename), (128, 64)).convert()
            img.set_colorkey(BLACK)
            self.level_signs.append(img)

        #buttons
        play_button = pygame.image.load(self.img_dir + "play_button.png").convert()
        self.play_button = pygame.transform.scale(play_button, (128, 64))
        self.play_button.set_colorkey(BLACK)

        play_button_hover = pygame.image.load(self.img_dir + "play_button_hover.png").convert()
        self.play_button_hover = pygame.transform.scale(play_button_hover, (128, 64))
        self.play_button_hover.set_colorkey(BLACK)

        exit_button = pygame.image.load(self.img_dir + "exit_button.png").convert()
        self.exit_button = pygame.transform.scale(exit_button, (128, 64))
        self.exit_button.set_colorkey(BLACK)

        exit_button_hover = pygame.image.load(self.img_dir + "exit_button_hover.png").convert()
        self.exit_button_hover = pygame.transform.scale(exit_button_hover, (128, 64))
        self.exit_button_hover.set_colorkey(BLACK)

        title_screen_button = pygame.image.load(self.img_dir + "title_screen_button_1.png").convert()
        self.title_screen_button = pygame.transform.scale(title_screen_button, (512, 64))
        self.title_screen_button.set_colorkey(BLACK)

        title_screen_button_hover = pygame.image.load(self.img_dir + "title_screen_button_2.png").convert()
        self.title_screen_button_hover = pygame.transform.scale(title_screen_button_hover, (512, 64))
        self.title_screen_button_hover.set_colorkey(BLACK)

    #get the tile map data
    def map_data(self):
        self.map = Map((self.map_dir + "tut_map.txt"))
        # self.map = Map((self.map_dir + "lvl_1_map.txt"))
        # self.map = Map((self.map_dir + "lvl_2_map.txt"))
        # self.map = Map((self.map_dir + "lvl_3_map.txt"))
        # self.map = Map((self.map_dir + "lvl_4_map.txt"))
        # self.map = Map((self.map_dir + "lvl_5_map.txt"))
        # self.map = Map((self.map_dir + "lvl_6_map.txt"))
        # self.map = Map((self.map_dir + "lvl_7_map.txt"))
        # self.map = Map((self.map_dir + "lvl_8_map.txt"))
        # self.map = Map((self.map_dir + "lvl_9_map.txt"))
        # self.map = Map((self.map_dir + "lvl_10_map.txt"))

    #create new instances of sprite classes
    def new(self):
        #sprite groups
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.tile_set = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        self.portals = pygame.sprite.Group()
        self.invis_block_1 = pygame.sprite.Group()
        self.invis_block_2 = pygame.sprite.Group()
        self.invis_block_3 = pygame.sprite.Group()
        self.invis_block_4 = pygame.sprite.Group()

        self.my_font = Font()

        #tilemap for sprites
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):

                if tile == "0":
                    #player
                    self.player = Player(self, col, row)

                elif tile == "1":
                    #floor
                    TileSet(self, col, row, 1)

                elif tile == "2":
                    #ceil
                    TileSet(self, col, row, 2)

                elif tile == "3":
                    #right wall
                    TileSet(self, col, row, 3)

                elif tile == "4":
                    #left wall
                    TileSet(self, col, row, 4)

                elif tile == "5":
                    #top right outside corner
                    TileSet(self, col, row, 5)

                elif tile == "6":
                    #top left outside corner
                    TileSet(self, col, row, 6)

                elif tile == "7":
                    #bottom right outside corner
                    TileSet(self, col, row, 7)

                elif tile == "8":
                    #bottom left outside corner
                    TileSet(self, col, row, 8)

                elif tile == "9":
                    #top right inside corner
                    TileSet(self, col, row, 9)

                elif tile == "a":
                    #top left inside corner
                    TileSet(self, col, row, "a")

                elif tile == "b":
                    #bottom right inside corner
                    TileSet(self, col, row, "b")

                elif tile == "c":
                    #bottom left inside corner
                    TileSet(self, col, row, "c")

                elif tile == "d":
                    #double inside corner (left)
                    TileSet(self, col, row, "d")

                elif tile == "e":
                    #double inside corner (right)
                    TileSet(self, col, row, "e")

                elif tile == "f":
                    #triple corner (left)
                    TileSet(self, col, row, "f")

                elif tile == "g":
                    #triple corner (right)
                    TileSet(self, col, row, "g")

                elif tile == "h":
                    #floor and ceiling
                    TileSet(self, col, row, "h")

                elif tile == "i":
                    #background greebling
                    TileSet(self, col, row, "i")

                elif tile == "j":
                    #background greebling and floor laser
                    TileSet(self, col, row, "i")
                    WallLaser(self, col, row, "floor")

                elif tile == "k":
                    #background greebling and ceiling laser
                    TileSet(self, col, row, "i")
                    WallLaser(self, col, row, "ceil")

                elif tile == "l":
                    #background greebling and right wall laser
                    TileSet(self, col, row, "i")
                    WallLaser(self, col, row, "right")

                elif tile == "m":
                    #background greebling and left wall laser
                    TileSet(self, col, row, "i")
                    WallLaser(self, col, row, "left")

                elif tile == "n":
                    #background greebling and top right corner lasers
                    TileSet(self, col, row, "i")
                    WallLaser(self, col, row, "ceil")
                    WallLaser(self, col, row, "right")

                elif tile == "o":
                    #background greebling and top left corner lasers
                    TileSet(self, col, row, "i")
                    WallLaser(self, col, row, "ceil")
                    WallLaser(self, col, row, "left")

                elif tile == "p":
                    #background greebling and bottom right corner lasers
                    TileSet(self, col, row, "i")
                    WallLaser(self, col, row, "floor")
                    WallLaser(self, col, row, "right")

                elif tile == "q":
                    #background greebling and bottom left corner lasers
                    TileSet(self, col, row, "i")
                    WallLaser(self, col, row, "floor")
                    WallLaser(self, col, row, "left")

                elif tile == "r":
                    #greebling high
                    TileSet(self, col, row, "r")

                elif tile == "s":
                    #greebling low
                    TileSet(self, col, row, "s")

                elif tile == "t":
                    #greebling
                    TileSet(self, col, row, "t")

                elif tile == "u":
                    #floor and top left inside corner
                    TileSet(self, col, row, "u")

                elif tile == "v":
                    #floor and top right inside corner
                    TileSet(self, col, row, "v")

                elif tile == "w":
                    #ceiling and bottom left inside corner
                    TileSet(self, col, row, "w")

                elif tile == "x":
                    #ceiling and bottom right inside corner
                    TileSet(self, col, row, "x")

                elif tile == "y":
                    #starting portal (green)
                    StartPortal(self, col, row)

                elif tile == "z":
                    #end portal (blue)
                    EndPortal(self, col, row)

                elif tile == "A":
                    #laser obstacle (when traveling to the right)
                    Lasers(self, col, row, "right")

                elif tile == "B":
                    #laser obstacle (when traveling to the left)
                    Lasers(self, col, row, "left")

                elif tile == "C":
                    #laser obstacle (when traveling up)
                    Lasers(self, col, row, "up")

                elif tile == "D":
                    #laser obstacle (when traveling down)
                    Lasers(self, col, row, "down")

                elif tile == "E":
                    #tutorial signs
                    if self.current_level == "tut":
                        TutorialSigns(self, col, row, "arrowkeys")

                    if self.current_level == "2":
                        TutorialSigns(self, col, row, "meters")

                    if self.current_level == "6":
                        TutorialSigns(self, col, row, "hint1")

                    if self.current_level == "8":
                        TutorialSigns(self, col, row, "hint2")

                    if self.current_level == "10":
                        TutorialSigns(self, col, row, "hint3")

                elif tile == "F":
                    #tutorial sign / sprites for other levels
                    TutorialSigns(self, col, row, "laser_tut")

                elif tile == "G":
                    #sign of current level
                    LevelSigns(self, col, row, self.current_level)

                elif tile == "H":
                    #laser rock
                    LaserRock(self, col, row)

                elif tile == "I":
                    #invisible block (order 1)
                    InvisibleBlock(self, col, row, "1")
                    TileSet(self, col, row, "i")

                elif tile == "J":
                    #invisible block (order 2)
                    InvisibleBlock(self, col, row, "2")
                    TileSet(self, col, row, "i")

                elif tile == "K":
                    #invisible block (order 3)
                    InvisibleBlock(self, col, row, "3")
                    TileSet(self, col, row, "i")

                elif tile == "L":
                    #invisible block (order 4)
                    InvisibleBlock(self, col, row, "4")
                    TileSet(self, col, row, "i")

                elif tile == "M":
                    #laser for the puzzle
                    if self.current_level == "6":
                        PuzzleLaser(self, col, row, "right")

                    if self.current_level == "7":
                        PuzzleLaser(self, col, row, "left")

                    if self.current_level == "8":
                        PuzzleLaser(self, col, row, "down")

                    if self.current_level == "10":
                        PuzzleLaser(self, col, row, "right")

        self.camera = Camera(self.map.width, self.map.height)

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

        #collision with lasers
        hits = pygame.sprite.spritecollide(self.player, self.lasers, False)
        if hits:
            self.playing = False
            self.reset()

        #collisions with end portals
        hits = pygame.sprite.spritecollide(self.player, self.portals, False)
        if hits:
            if self.current_level == "tut":
                self.playing = False
                self.reset()
                self.current_level = "1"
                self.map = Map((self.map_dir + "lvl_1_map.txt"))

            elif self.current_level == "1":
                self.playing = False
                self.reset()
                self.current_level = "2"
                self.map = Map((self.map_dir + "lvl_2_map.txt"))

            elif self.current_level == "2":
                self.playing = False
                self.reset()
                self.current_level = "3"
                self.map = Map((self.map_dir + "lvl_3_map.txt"))

            elif self.current_level == "3":
                self.playing = False
                self.reset()
                self.current_level = "4"
                self.map = Map((self.map_dir + "lvl_4_map.txt"))

            elif self.current_level == "4":
                self.playing = False
                self.reset()
                self.current_level = "5"
                self.map = Map((self.map_dir + "lvl_5_map.txt"))

            elif self.current_level == "5":
                self.playing = False
                self.reset()
                self.current_level = "6"
                self.map = Map((self.map_dir + "lvl_6_map.txt"))

            elif self.current_level == "6":
                self.playing = False
                self.reset()
                self.current_level = "7"
                self.map = Map((self.map_dir + "lvl_7_map.txt"))

            elif self.current_level == "7":
                self.playing = False
                self.reset()
                self.current_level = "8"
                self.map = Map((self.map_dir + "lvl_8_map.txt"))

            elif self.current_level == "8":
                self.playing = False
                self.reset()
                self.current_level = "9"
                self.map = Map((self.map_dir + "lvl_9_map.txt"))

            elif self.current_level == "9":
                self.playing = False
                self.reset()
                self.current_level = "10"
                self.map = Map((self.map_dir + "lvl_10_map.txt"))

            elif self.current_level == "10":
                self.playing = False
                self.reset()
                self.current_level = "tut"
                self.map = Map((self.map_dir + "tut_map.txt"))
                self.end_cutscene()

        #collision with puzzle mechanics
        if self.collide_1:
            hits = pygame.sprite.spritecollide(self.player, self.invis_block_1, False)
            if hits:
                if self.player.sequence == "":
                    self.player.sequence = "1"
                    self.collide_1 = False
                else:
                    self.playing = False
                    self.reset()

        if self.collide_2:
            hits = pygame.sprite.spritecollide(self.player, self.invis_block_2, False)
            if hits:
                if self.player.sequence == "1":
                    self.player.sequence = "2"
                    self.collide_2 = False
                else:
                    self.playing = False
                    self.reset()

        if self.collide_3:
            hits = pygame.sprite.spritecollide(self.player, self.invis_block_3, False)
            if hits:
                if self.player.sequence == "2":
                    self.player.sequence = "3"
                    self.collide_3 = False
                else:
                    self.playing = False
                    self.reset()

        if self.collide_4:
            hits = pygame.sprite.spritecollide(self.player, self.invis_block_4, False)
            if hits:
                if self.player.sequence == "3":
                    self.player.sequence = ""
                    self.solved = True
                    self.collide_4 = False
                else:
                    self.playing = False
                    self.reset()

    #event handler
    def events(self):
        for event in pygame.event.get():

            #if the exit button is pressed
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            #if a key is pressed down
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.playing:
                        self.playing = False
                    self.running = False

                if event.key == pygame.K_LSHIFT:
                    if not self.player.is_slowing and not self.recharge_boost:
                        self.player.is_boosting = True

                if event.key == pygame.K_LCTRL:
                    if not self.player.is_boosting and not self.recharge_slow:
                        self.player.is_slowing = True

                if event.key == pygame.K_SPACE and self.counting and not self.player.spawn:
                    self.playing = False
                    self.reset()

                if event.key == pygame.K_SPACE:
                    self.space_holding = True

            #if a key is released
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                     self.counting = True
                     self.space_holding = False
                     self.space_hold_counter = 0

        #handling events related to bugs
        if not self.player.spawn:
            if self.space_holding:
                self.space_hold_counter += 1

                if self.space_hold_counter > 50:
                    self.playing = False
                    self.reset()

            if self.counting:
                self.counter += 1

                if self.counter > 7:
                    self.counting = False
                    self.counter = 0

            #move text when player moves (on the tutorial level)
            self.initial_y += 1

            if self.initial_y > HEIGHT + 50:
                self.initial_y = HEIGHT + 50

    def draw(self):
        self.screen.fill(BKGD_COLOR)

        #draw all the sprites in the all_sprites group
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        if (self.current_level == "tut"):
            self.my_font.render(self.screen, "note: you don't have to hold the key down", (30, self.initial_y))

        if (self.current_level != "tut" and self.current_level != "1"):
            #draw the boost and slow meter
            self.screen.blit(self.boost_meter, (WIDTH - 128, 16))
            self.screen.blit(self.slow_meter, (WIDTH - 128, 96))

            pygame.draw.rect(self.screen, BOOST_BAR, (self.boost, 36, 80, 32))
            pygame.draw.rect(self.screen, SLOW_BAR, (self.slow, 116, 80, 32))

            #text
            self.my_font.render(self.screen, "Boost Meter", (WIDTH - 90, 16))
            self.my_font.render(self.screen, "Slow Meter", (WIDTH - 90, 96))

        if (self.current_level == "2"):
            self.my_font.render(self.screen, "note: do NOT hold or spam the space bar!", (300, HEIGHT - 280))
            self.my_font.render(self.screen, "press shift to boost!", (40, HEIGHT - 253))
            self.my_font.render(self.screen, "press ctrl to slow down!", (40, HEIGHT - 193))
            self.my_font.render(self.screen, "note: when you boost or slow down,", (20, HEIGHT - 85))
            self.my_font.render(self.screen, "it is for a set duration, indicated", (20, HEIGHT - 65))
            self.my_font.render(self.screen, "on the meter.", (20, HEIGHT - 45))

        pygame.display.flip()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def title_screen(self):
        self.title_screen_loop = True
        self.title_screen_map = Map("data/maps/title_map.txt")
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.cursor_group = pygame.sprite.Group()
        self.tile_set = pygame.sprite.Group()
        self.demo_portal = pygame.sprite.Group()

        self.my_font = Font()
        Cursor(self)

        for row, tiles in enumerate(self.title_screen_map.data):
            for col, tile in enumerate(tiles):

                if tile == "1":
                    PlayButton(self, col, row)

                if tile == "2":
                    ExitButton(self, col, row)

                if tile == "3":
                    TileSet(self, col, row, 1)

                if tile == "4":
                    TileSet(self, col, row, "s")

                if tile == "5":
                    TileSet(self, col, row, "r")

                if tile == "6":
                    TileSet(self, col, row, "t")

                if tile == "7":
                    DemoPlayer(self, col,row, "title_screen")

                if tile == "8":
                    DemoPortal(self, col, row)

        while self.title_screen_loop:
            self.clock.tick(FPS)

            self.screen.fill(BKGD_COLOR)
            self.all_sprites.draw(self.screen)
            self.screen.blit(self.logo, (270, -40))
            self.my_font.render(self.screen, "Alpha 1.0", (WIDTH - 70, 10))
            self.cursor_group.draw(self.screen)

            self.all_sprites.update()
            self.cursor_group.update()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.title_screen_loop = False
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.title_screen_loop = False
                        self.running = False

    def intro_cutscene(self):
        self.cutscene_loop_2 = True
        self.intro_cutscene_map = Map("data/maps/intro_cutscene.txt")
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.tile_set = pygame.sprite.Group()
        self.demo_portal = pygame.sprite.Group()

        self.my_font = Font()

        red_bkgd = pygame.Surface((WIDTH, HEIGHT))
        red_bkgd.fill((239, 35, 60))
        red_bkgd.set_alpha(25)

        for row, tiles in enumerate(self.intro_cutscene_map.data):
            for col, tile in enumerate(tiles):

                if tile == "0":
                    self.demo_player_2 = DemoPlayer(self, col, row, "intro_cutscene")

                elif tile == "1":
                    #floor
                    TileSet(self, col, row, 1)

                elif tile == "2":
                    #ceil
                    TileSet(self, col, row, 2)

                elif tile == "3":
                    #right wall
                    TileSet(self, col, row, 3)

                elif tile == "4":
                    #left wall
                    TileSet(self, col, row, 4)

                elif tile == "5":
                    #top right outside corner
                    TileSet(self, col, row, 5)

                elif tile == "6":
                    #top left outside corner
                    TileSet(self, col, row, 6)

                elif tile == "7":
                    #bottom right outside corner
                    TileSet(self, col, row, 7)

                elif tile == "8":
                    #bottom left outside corner
                    TileSet(self, col, row, 8)

                elif tile == "9":
                    #top right inside corner
                    TileSet(self, col, row, 9)

                elif tile == "a":
                    #top left inside corner
                    TileSet(self, col, row, "a")

                elif tile == "b":
                    #bottom right inside corner
                    TileSet(self, col, row, "b")

                elif tile == "c":
                    #bottom left inside corner
                    TileSet(self, col, row, "c")

                elif tile == "d":
                    #background greebling
                    TileSet(self, col, row, "i")

                elif tile == "e":
                    #greebling high
                    TileSet(self, col, row, "r")

                elif tile == "f":
                    #greebling low
                    TileSet(self, col, row, "s")

                elif tile == "g":
                    #greebling
                    TileSet(self, col, row, "t")

                elif tile == "h":
                    DemoPortal(self, col, (row - 0.5))

        self.camera = Camera(self.intro_cutscene_map.width, self.intro_cutscene_map.height)

        while self.cutscene_loop_2:
            self.clock.tick(FPS)

            self.screen.fill(BKGD_COLOR)
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, self.camera.apply(sprite))

            if self.demo_player_2.human_frame_counter > 44 and self.demo_player_2.human_frame_counter < 110:
                self.screen.blit(red_bkgd, (0, 0))

            if self.demo_player_2.human_frame_counter > 160 and self.demo_player_2.human_frame_counter < 230:
                self.my_font.render(self.screen, "Ow!", (250, 330))

            if self.demo_player_2.human_frame_counter > 300 and self.demo_player_2.human_frame_counter < 375:
                self.my_font.render(self.screen, "I fell pretty hard", (200, 330))

            if self.demo_player_2.human_frame_counter > 630 and self.demo_player_2.human_frame_counter < 690:
                self.my_font.render(self.screen, "Where am I?", (475, 330))

            if self.demo_player_2.human_frame_counter > 760 and self.demo_player_2.human_frame_counter < 835:
                self.my_font.render(self.screen, "I think I'm lost", (460, 330))

            if self.demo_player_2.human_frame_counter > 1125 and self.demo_player_2.human_frame_counter < 1200:
                self.my_font.render(self.screen, "A portal?", (690, 330))

            if self.demo_player_2.human_frame_counter > 1275 and self.demo_player_2.human_frame_counter < 1350:
                self.my_font.render(self.screen, "Where does it go?", (670, 330))

            if self.demo_player_2.human_frame_counter > 1425 and self.demo_player_2.human_frame_counter < 1500:
                self.my_font.render(self.screen, "Time to find out!", (670, 330))

            pygame.draw.rect(self.screen, BLACK, (0, 0, self.intro_cutscene_map.width, 128))
            pygame.draw.rect(self.screen, BLACK, (0, HEIGHT - 128, self.intro_cutscene_map.width, 128))

            self.all_sprites.update()
            self.camera.update(self.demo_player_2)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cutscene_loop_2 = False
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.cutscene_loop_2 = False
                        self.running = False

    def end_cutscene(self):
        self.cutscene_loop_1 = True
        self.end_cutscene_map = Map((self.map_dir + "ending_cutscene.txt"))
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.tile_set = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        self.demo_portal = pygame.sprite.Group()
        self.cursor_group = pygame.sprite.Group()
        self.button = pygame.sprite.Group()

        Cursor(self)
        TitleScreenButton(self, 300, 370)

        self.my_font = Font()

        self.game_over = False

        red_bkgd = pygame.Surface((WIDTH, HEIGHT))
        red_bkgd.fill((239, 35, 60))
        red_bkgd.set_alpha(150)

        for row, tiles in enumerate(self.end_cutscene_map.data):
            for col, tile in enumerate(tiles):

                if tile == "0":
                    self.demo_player = DemoPlayer(self, (col - 10), row, "end_cutscene")

                elif tile == "1":
                    #floor
                    TileSet(self, col, row, 1)

                elif tile == "2":
                    #ceil
                    TileSet(self, col, row, 2)

                elif tile == "3":
                    #right wall
                    TileSet(self, col, row, 3)

                elif tile == "4":
                    #left wall
                    TileSet(self, col, row, 4)

                elif tile == "5":
                    #top right outside corner
                    TileSet(self, col, row, 5)

                elif tile == "6":
                    #top left outside corner
                    TileSet(self, col, row, 6)

                elif tile == "7":
                    #bottom right outside corner
                    TileSet(self, col, row, 7)

                elif tile == "8":
                    #bottom left outside corner
                    TileSet(self, col, row, 8)

                elif tile == "9":
                    #top right inside corner
                    TileSet(self, col, row, 9)

                elif tile == "a":
                    #top left inside corner
                    TileSet(self, col, row, "a")

                elif tile == "b":
                    #bottom right inside corner
                    TileSet(self, col, row, "b")

                elif tile == "c":
                    #bottom left inside corner
                    TileSet(self, col, row, "c")

                elif tile == "d":
                    #background greebling
                    TileSet(self, col, row, "i")

                elif tile == "e":
                    #background greebling and floor laser
                    TileSet(self, col, row, "i")
                    WallLaser(self, col, row, "floor")

                elif tile == "f":
                    #background greebling and ceiling laser
                    TileSet(self, col, row, "i")
                    WallLaser(self, col, row, "ceil")

                elif tile == "g":
                    DemoPortal(self, col, (row - 0.5))

                elif tile == "h":
                    InvisibleBridge(self, col, row)
                    TileSet(self, col, row, "i")
                    TileSet(self, col + 2, row, "i")
                    Bridge(self, col, row)

        self.camera = Camera(self.end_cutscene_map.width, self.end_cutscene_map.height)

        while self.cutscene_loop_1:
            self.clock.tick(FPS)

            self.screen.fill(BKGD_COLOR)

            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, self.camera.apply(sprite))

            if self.demo_player.human_frame_counter > 250 and self.demo_player.human_frame_counter < 325:
                self.my_font.render(self.screen, "Am I free?", (490, 330))

            if self.demo_player.human_frame_counter > 400 and self.demo_player.human_frame_counter < 475:
                self.my_font.render(self.screen, "Clearly, I'm not", (470, 330))

            if self.demo_player.human_frame_counter > 550 and self.demo_player.human_frame_counter < 625:
                self.my_font.render(self.screen, "Where am I?", (480, 330))

            if self.demo_player.human_frame_counter > 750 and self.demo_player.human_frame_counter < 825:
                self.my_font.render(self.screen, "A bridge?", (665, 330))

            pygame.draw.rect(self.screen, BLACK, (0, 0, self.end_cutscene_map.width, 128))
            pygame.draw.rect(self.screen, BLACK, (0, HEIGHT - 128, self.end_cutscene_map.width, 128))

            if self.game_over:
                self.screen.blit(red_bkgd, (0, 0))
                self.screen.blit(self.death_text, (300, 100))
                self.my_font.render(self.screen, "If you are reading this, it means you reached the end.", (380, 250))
                self.my_font.render(self.screen, "It was a fun journey getting here and I'm glad I get to", (370, 280))
                self.my_font.render(self.screen, "end it off with a bang, literally.", (450, 310))
                self.my_font.render(self.screen, "p.s. the next time you walk on a bridge, this will happen to you", (340, 450))
                self.button.draw(self.screen)
                self.cursor_group.draw(self.screen)

            self.all_sprites.update()
            self.cursor_group.update()
            self.button.update()
            self.camera.update(self.demo_player)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cutscene_loop_1 = False
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.cutscene_loop_1 = False
                        self.running = False

g = Game()

g.title_screen()

while g.running:
    g.new()
    g.run()

pygame.quit()
sys.exit()
