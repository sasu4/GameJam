import pygame
import random
from os import listdir
from os.path import isfile, join

pygame.init()
pygame.display.set_caption('Hra')

WIDTH, HEIGHT = 800, 600
FPS = 60
VELOCITY = 5 # 5
main_menu = True
tutorial = False
game_over = False
winner = False

window = pygame.display.set_mode((WIDTH, HEIGHT))

bkg_image = pygame.image.load('assets/menu.png')
bkg_image = pygame.transform.scale(bkg_image, (WIDTH, HEIGHT))
bkg_gameover = pygame.image.load('assets/gameover.png')
bkg_gameover = pygame.transform.scale(bkg_gameover, (WIDTH, HEIGHT))
bkg_winner = pygame.image.load('assets/winner.png')
bkg_winner = pygame.transform.scale(bkg_winner, (WIDTH, HEIGHT))
start_image = pygame.image.load('assets/startbtn.png')
exit_image = pygame.image.load('assets/exitbtn.png')
restart_image = pygame.image.load('assets/restartbtn.png')
tutorial_image = pygame.image.load('assets/tutorialbtn.png')
tutorial_background = pygame.image.load('assets/tutos.png')
full_heart_image = pygame.image.load('assets/Icons/HeartFull.png')
half_heart_image = pygame.image.load('assets/Icons/HeartHalf.png')
empty_heart_image = pygame.image.load('assets/Icons/HeartEmpty.png')


class Button():
    def __init__(self, x, y, image):
        self.image = pygame.transform.scale(image, (140, 60))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        window.blit(self.image, self.rect)
        return action

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheet(dir1, dir2, w, h):
    path = join("assets", dir1, dir2)
    images = [file for file in listdir(path) if isfile(join(path, file))]
    all_sprites = {}
    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        sprites = []
        for i in range(sprite_sheet.get_width() // w):
            surface = pygame.Surface((w, h), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * w, 0, w, h)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        all_sprites[image.replace(".png", "")] = sprites
    return all_sprites

class Hero(pygame.sprite.Sprite):
    GRAVITY = 1
    SPRITES = load_sprite_sheet("hero", "", 24, 24)
    ANIMATION_DELAY = 5
    global main_menu

    def __init__(self, x, y, w, h):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.life = 100
        self.last_hit_object = None

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self, object):
        global game_over
        self.hit = True
        if self.last_hit_object != object:
            self.life -= 10
            self.last_hit_object = object
        if self.life == 0:
            game_over = True
        self.hit_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps *2:
            self.hit = False
            self.hit_count = 0
        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hurt"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "jump"
        elif self.x_vel != 0:
            sprite_sheet = "run"
        sprite_sheet_name = sprite_sheet
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, window, offset_x):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))


def get_block(size, x, y):
    path = join("assets", "terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(x, y, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size, 0, 0)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Food(Object):
    ANIMATION_DELAY = 3
    def __init__(self, x, y, w, h, type, dir, parameter):
        super().__init__(x, y, w, h, type)
        self.trap = load_sprite_sheet("food", dir, w, h)
        self.image = self.trap[parameter][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = parameter

    def loop(self):
        sprites = self.trap[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(sprite):
    image = pygame.image.load(join("assets", "background", sprite))
    _, _, w, h = image.get_rect()
    tiles = []
    for i in range(WIDTH // w + 1):
        for j in range(HEIGHT // h + 1):
            pos = [i * w, j * h]
            tiles.append(pos)
    return tiles, image


def draw(window, background, bg_image, hero, objects=None, offset_x=0):
    for tile in background:
        window.blit(bg_image, tuple(tile))
    for obj in objects:
        obj.draw(window, offset_x)
    hero.draw(window, offset_x)
    # hearts
    draw_hearts(window, hero)
    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
            collided_objects.append(obj)
    return collided_objects



def collide(player, objects, dx):
    player.move(dx*2, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    player.move(-dx*2, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    global main_menu, VELOCITY, winner
    keys = pygame.key.get_pressed()

    collide_left = collide(player, objects, -VELOCITY *2)
    collide_right = collide(player, objects, VELOCITY *2)

    #if keys[pygame.K_LEFT] and not collide_left:
    #    player.move_left(VELOCITY)
    #if keys[pygame.K_RIGHT] and not collide_right:
    #    player.move_right(VELOCITY)
    if not collide_right:
        player.move_right(VELOCITY)
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)

    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "saw":
            player.make_hit(obj)
        if obj and obj.name == "fire":
            player.make_hit(obj)
        if obj and obj.name == "spike":
            player.make_hit(obj)


def draw_hearts(window, hero):
    if hero.life == 100:
        window.blit(full_heart_image, (hero.x_vel, 10))
        window.blit(full_heart_image, (hero.x_vel + 45, 10))
        window.blit(full_heart_image, (hero.x_vel + 45 * 2, 10))
        window.blit(full_heart_image, (hero.x_vel + 45 * 3, 10))
        window.blit(full_heart_image, (hero.x_vel + 45 * 4, 10))
    elif hero.life == 90:
        window.blit(full_heart_image, (hero.x_vel, 10))
        window.blit(full_heart_image, (hero.x_vel + 45, 10))
        window.blit(full_heart_image, (hero.x_vel + 45 * 2, 10))
        window.blit(full_heart_image, (hero.x_vel + 45 * 3, 10))
        window.blit(half_heart_image, (hero.x_vel + 45 * 4, 10))
    elif hero.life == 80:
        window.blit(full_heart_image, (hero.x_vel, 10))
        window.blit(full_heart_image, (hero.x_vel + 45, 10))
        window.blit(full_heart_image, (hero.x_vel + 45 * 2, 10))
        window.blit(full_heart_image, (hero.x_vel + 45 * 3, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 4, 10))
    elif hero.life == 70:
        window.blit(full_heart_image, (hero.x_vel, 10))
        window.blit(full_heart_image, (hero.x_vel + 45, 10))
        window.blit(full_heart_image, (hero.x_vel + 45 * 2, 10))
        window.blit(half_heart_image, (hero.x_vel + 45 * 3, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 4, 10))
    elif hero.life == 60:
        window.blit(full_heart_image, (hero.x_vel, 10))
        window.blit(full_heart_image, (hero.x_vel + 45, 10))
        window.blit(full_heart_image, (hero.x_vel + 45 * 2, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 3, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 4, 10))
    elif hero.life == 50:
        window.blit(full_heart_image, (hero.x_vel, 10))
        window.blit(full_heart_image, (hero.x_vel + 45, 10))
        window.blit(half_heart_image, (hero.x_vel + 45 * 2, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 3, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 4, 10))
    elif hero.life == 40:
        window.blit(full_heart_image, (hero.x_vel, 10))
        window.blit(full_heart_image, (hero.x_vel + 45, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 2, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 3, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 4, 10))
    elif hero.life == 30:
        window.blit(full_heart_image, (hero.x_vel, 10))
        window.blit(half_heart_image, (hero.x_vel + 45, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 2, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 3, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 4, 10))
    elif hero.life == 20:
        window.blit(full_heart_image, (hero.x_vel, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 2, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 3, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 4, 10))
    elif hero.life == 10:
        window.blit(half_heart_image, (hero.x_vel, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 2, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 3, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 4, 10))
    elif hero.life == 0:
        window.blit(empty_heart_image, (hero.x_vel, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 2, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 3, 10))
        window.blit(empty_heart_image, (hero.x_vel + 45 * 4, 10))


def main(window):
    global main_menu, tutorial, game_over, winner, VELOCITY
    clock = pygame.time.Clock()
    background, bg_image = get_background("Yellow.png")

    block_size = 96
    hero = Hero(100,100, 50, 50)
    floor = []
    objects = []

    offset_x = 0
    scroll_area_width = 200

    start_button = Button(WIDTH // 2 - 250, HEIGHT // 2, start_image)
    exit_button = Button(WIDTH // 2 + 150, HEIGHT // 2, exit_image)
    tutorial_button = Button(WIDTH // 2-60, HEIGHT // 2 + 150, tutorial_image)
    restart_button = Button(WIDTH //2 - 100, HEIGHT // 2, restart_image)


    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN and main_menu == False:
                if event.key == pygame.K_SPACE and hero.jump_count < 1:
                    hero.jump()
                if event.key == pygame.K_p:
                    main_menu = True
        if main_menu == True:
            window.blit(bkg_image, (0, 0)) # start menu bkgnd
            if exit_button.draw():
                run = False
                break
            if tutorial_button.draw():
                main_menu = False
                tutorial = True
            if start_button.draw():
                offset_x = 0
                hero.rect.x = 0
                food = [Food(i * 500, HEIGHT - block_size - 64 - 19, 38, 38, "saw", "Saw", "on") for i in
                            range(2, 10)]
                floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in
                             range(-WIDTH // block_size, WIDTH * 10 // block_size)]

                objects = [*floor, *food]
                main_menu = False
            pygame.display.update()
        elif tutorial == True and main_menu == False:
            window.blit(tutorial_background, (0, 0))
            if start_button.draw():
                offset_x = 0
                hero.rect.x = 0
                food = [Food(i * 500, HEIGHT - block_size - 64 - 19, 38, 38, "saw", "Saw", "on") for i in
                        range(2, 10)]
                floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in
                         range(-WIDTH // block_size, WIDTH * 10 // block_size)]
                objects = [*floor, *food]
                main_menu = False
                tutorial = False
            pygame.display.flip()
        elif game_over == True:
            window.blit(bkg_gameover, (0, 0))  # start menu bkgnd
            if restart_button.draw():
                main_menu = True
                game_over = False
                hero.life = 100
                VELOCITY = 5
            pygame.display.update()
        elif winner == True:
            window.blit(bkg_winner, (0, 0))  # start menu bkgnd
            if restart_button.draw():
                main_menu = True
                winner = False
                hero.life = 100
                VELOCITY = 5
            pygame.display.update()
        else:
            hero.loop(FPS)
            for f in food:
                f.loop()
            handle_move(hero, objects)
            draw(window, background, bg_image, hero, objects, offset_x)
            if ((hero.rect.right - offset_x >= WIDTH - scroll_area_width) and (hero.x_vel > 0)) or (
                (hero.rect.left - offset_x <= scroll_area_width) and (hero.x_vel < 0)):
                offset_x += hero.x_vel

    pygame.quit()


if __name__ == "__main__":
    main(window)