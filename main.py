import pygame
import os
import time
import random
import numpy as np
from moviepy.editor import *
from moviepy.video.tools.drawing import color_gradient


horizon = 350
vertical = 150
os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (horizon, vertical) # Positions game WIN

pygame.font.init()
WIDTH = 750  # Window WIDTH
HEIGHT = 750  # Window HEIGHT
WIN = pygame.display.set_mode([WIDTH, HEIGHT])  # Displays game window to the screen
pygame.display.set_caption("STAR_WARS edition --> Space Invaders")
ICON = pygame.image.load(os.path.join("assets", "x_wing_small.png"))
pygame.display.set_icon(ICON)
#  LOAD IMAGES
BACKGROUND = pygame.image.load(os.path.join("assets", "background-black.png"))
#  STAR_WARS
STAR_WARS = pygame.image.load(os.path.join("assets", "starwars.png"))
# SPACESHIP IMAGES
millenium_falcon = pygame.image.load(os.path.join("assets", "millenium_falcon2.png"))
death_star = pygame.image.load(os.path.join("assets", "deathStar.png"))
star_destroyer = pygame.image.load(os.path.join("assets", "star_destroyer.png"))
tie_fighter = pygame.image.load(os.path.join("assets", "tie_fighter.png"))
x_wing = pygame.image.load(os.path.join("assets", "x_wing.png"))

#  LASER IMAGES
blue_laser = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
green_laser = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
red_laser = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
yellow_laser = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

#  CHARACTERS IMAGES
c3po = pygame.image.load(os.path.join("assets", "c3po.png"))
cylon_head = pygame.image.load(os.path.join("assets", "cylonHead.png"))
skywalker = pygame.image.load(os.path.join("assets", "lukeSkywalker.png"))
r2 = pygame.image.load(os.path.join("assets", "r2d2.png"))
vader = pygame.image.load(os.path.join("assets", "vader.png"))
# vader64 = pygame.image.load(os.path.join("assets", "vader64.png"))
yoda = pygame.image.load(os.path.join("assets", "yoda.png"))

BG = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT))

# TODO Create STAR_WARS crawl in FX for game intro

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0  # Prohibits player to SPAM laser

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)


    def cooldown(self): # Function to handle cool_down_timer b/t available LASER shots
        if self.cool_down_counter >= self.COOLDOWN: # IF timer reaches .5sec ->
            self.cool_down_counter = 0 # Resets timer back to ZERO
        elif self.cool_down_counter > 0: # ELIF timer is > ZERO ->
            self.cool_down_counter += 1 # ADD 1 to timer

    def shoot(self): # Function to handle LASER creation
        if self.cool_down_counter == 0: # IF cool_down_timer B/T laser shots == 0
            laser = Laser(self.x, self.y, self.laser_img)  # Creates new LASER object
            self.lasers.append(laser)  # Appends LASER object to lasers[]
            self.cool_down_counter = 1 # Starts timer

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = millenium_falcon
        self.laser_img = blue_laser
        self.mask = pygame.mask.from_surface(self.ship_img)  # Mask is used for collision
        self.max_health = health

    def move_lasers(self, vel, objs): # Moves each LASER & tests ENEMY(OBJ) collision ->
        self.cooldown() # Increments TIMER & Checks if LASER can be shot ->
        for laser in self.lasers: # FOR each LASER that exits in our lasers[] ->
            laser.move(vel*2) # Move each LASER  ->
            if laser.off_screen(HEIGHT): # IF Laser is off the screen ->
                self.lasers.remove(laser) # REMOVES laser from the lasers[]
            else:
                for obj in objs: # FOR each ENEMY in ENEMIES[] test ->
                    if laser.collision(obj): # IF LASER collides w/ ENEMY(obj) ->
                        objs.remove(obj) # REMOVE ENEMY from ENEMIES[] ->
                        self.lasers.remove(laser) # REMOVES LASER from lasers[]

    def draw(self, window):
        super(Player, self).draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
                "red": (tie_fighter, red_laser),
                "green": (star_destroyer, red_laser),
                "blue": (death_star, red_laser)
                }

    easy = tie_fighter, red_laser
    medium = star_destroyer, red_laser
    hard = death_star, red_laser
    red = red_laser

    def __init__(self, x, y, rank, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[rank]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self): # Function to handle LASER creation
        if self.cool_down_counter == 0: # IF cool_down_timer B/T laser shots == 0
            laser = Laser(self.x-10, self.y, self.laser_img)  # Creates new LASER object
            self.lasers.append(laser)  # Appends LASER object to lasers[]
            self.cool_down_counter = 1 # Starts timer

    def move_lasers(self, vel, obj): # () to move LASERS & check for collsion b/t OBJECTS
        self.cooldown() # Increments TIMER & Checks if LASER can be shot
        for laser in self.lasers: # FOR each LASER that exits in our lasers[] ->
            laser.move(vel - 5) # Moves each LASER obj ->
            if laser.off_screen(HEIGHT): # IF Laser is off the screen ->
                self.lasers.remove(laser) # REMOVES laser from the lasers[]
            elif laser.collision(obj): # IF LASER collides w/ obj ->
                obj.health -= 10 # SUBTRACTS 10 from OBJ passed to through (params) ->
                self.lasers.remove(laser) # REMOVES LASER from lasers[]


    def cooldown(self): # Function to handle cool_down_timer b/t available LASER shots
        if self.cool_down_counter >= self.COOLDOWN: # IF timer reaches .5sec ->
            self.cool_down_counter = 0 # Resets timer back to ZERO
        elif self.cool_down_counter > 0: # ELIF timer is > ZERO ->
            self.cool_down_counter += 1 # ADD 1 to timer

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x # Tells us distance b/t xcor's of OBJ1 & OBJ2
    offset_y = obj2.y - obj1.y # Tell us distance b/t ycor's of OBJ1 & OBJ2
    # RETURN'S TRUE when obj1(LASER)'s mask overlaps obj2(SHIP)'s mask
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None # != NONE return's (x,y)coords

#  GAME LOOP
def main():
    run = True
    FPS = 60
    level = 1
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5 # How fast MIL FALCON can move
    laser_vel = 10 # How fast FALCON'S lasers move

    player = Player(350, 630)

    clock = pygame.time.Clock()
    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))
        # draw text to window
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 20))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies: # For each enemy generated ->
            enemy.draw(WIN)  # Draw enemy to the screen

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("YOU LOST !!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()



    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue


        for i in range(wave_length):
            if len(enemies) <= wave_length:
                rand_Ycor = random.randrange(-500, -50)
                rand_Xcor = random.randrange(50, WIDTH-100)
                # enemy = Enemy(rand_Xcor, rand_Ycor, "red")
                enemy = Enemy(rand_Xcor, rand_Ycor, random.choice(["red", "green", "blue"]))
                enemies.append(enemy)



        # Logic to print waves of Random enemies
        if len(enemies) == 0: # IF all enemies killed ->
            level += 1 # Add 1 to Level ->
            wave_length += 5 # +5 enemies, +'s difficulty to next level


        for event in pygame.event.get():  # Checks for quit button
            if event.type == pygame.QUIT:
                quit()


        keys = pygame.key.get_pressed()  # Sets KEYBINDINGS to variable KEYS
        if keys[pygame.K_d] and player.x - player_vel > 0:  # LEFT & sets left window boundary
            player.x -= player_vel
        if keys[pygame.K_f] and player.x + player_vel + player.get_width() < WIDTH:  # RIGHT & sets right window boundary
            player.x += player_vel
        if keys[pygame.K_j] and player.y - player_vel > 0:  # UP & sets window boundary
            player.y -= player_vel
        if keys[pygame.K_k] and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # DOWN & sets window
            # boundary
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]: # Python slang to make a copy of a list ->
            enemy.move(enemy_vel) # Moves each Enemy in the wave
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*120) == 1: # How often does ENEMY randomly ->
                enemy.shoot()  # Shoot LASER

            if collide(enemy, player): # IF MILLENIUM FALCON(PLAYER) collides w/ ENEMY ->
                player.health -=10  # MILLENIUM FALCON(PLAYER) health - 10 ->
                enemies.remove(enemy)  # Remove ENEMY from enemies[]
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy) # Removes enemy Object from the list of enemies
        player.move_lasers(-laser_vel, enemies)
def main_menu():
    mayTheForce_font = pygame.font.SysFont("comicsans", 50)
    title_font = pygame.font.SysFont("comicsans", 35)

    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Click Mouse to Begin...", 1, (255, 255, 255))
        mayTheForceFont_label = mayTheForce_font.render("May the force be with YOU...", 1, (255, 255, 255))

        WIN.blit(STAR_WARS, (WIDTH/2 - STAR_WARS.get_width()/2, 50))
        WIN.blit(mayTheForceFont_label, (WIDTH/2 - mayTheForceFont_label.get_width()/2, 200))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()
