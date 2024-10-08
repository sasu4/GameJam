import pygame
import random
from os import listdir
from os.path import isfile, join

pygame.init()
pygame.display.set_caption('Hungry Hedgie')

WIDTH, HEIGHT = 800, 600
FPS = 60
VELOCITY = 5
main_menu = True
tutorial = False
game_over = False
winner = False
contin = False # continue game
level = 1

window = pygame.display.set_mode((WIDTH, HEIGHT))

bkg_image = pygame.image.load('assets/background/menu.png')
bkg_image = pygame.transform.scale(bkg_image, (WIDTH, HEIGHT))
bkg_gameover = pygame.image.load('assets/background/gameover.png')
bkg_gameover = pygame.transform.scale(bkg_gameover, (WIDTH, HEIGHT))
bkg_winner = pygame.image.load('assets/background/winner.png')
bkg_winner = pygame.transform.scale(bkg_winner, (WIDTH, HEIGHT))
start_image = pygame.image.load('assets/buttons/startbtn.png')
exit_image = pygame.image.load('assets/buttons/exitbtn.png')
continue_image = pygame.image.load('assets/buttons/continuebtn.png')
restart_image = pygame.image.load('assets/buttons/restartbtn.png')
tutorial_image = pygame.image.load('assets/buttons/tutorialbtn.png')
tutorial_background = pygame.image.load('assets/background/tutos.png')
tutorial_background = pygame.transform.scale(tutorial_background, (WIDTH, HEIGHT))


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
            sprites.append(pygame.transform.scale(surface, (rect.width*4, rect.height*4)))
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
        self.default_width = w
        self.default_height = h
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.radius = 1
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
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

    def make_hit(self, object, type):
        global game_over, GRAVITY, level, contin
        self.hit = True
        if (self.last_hit_object != object) and (type == 'good'):
            self.GRAVITY -= 0.05
            self.last_hit_object = object
            self.radius += 5
        elif (self.last_hit_object != object) and (type == 'bad'):
            self.GRAVITY += 0.1
            self.last_hit_object = object
            self.radius -= 10
            if self.rect.height < 30:
                game_over = True
                contin = False
                level = 1
        self.hit_count = 0
        object.update()

    def move_right(self, vel):
        self.x_vel = vel
        self.animation_count = 0

    def loop(self, fps):
        global game_over, winner, level, main_menu, contin
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0
        if self.rect.x > 23000:
            game_over = True
            contin = False
        if (self.rect.height >= 110) and (level == 1):
            level += 1
            main_menu = True
            contin = True
        elif (self.rect.height >= 115) and (level == 2):
            level += 1
            main_menu = True
            contin = True
        elif (self.rect.height >= 125) and (level == 3):
            level += 1
            main_menu = True
            contin = True
        elif (self.rect.height >= 130) and (level == 4):
            level += 1
            main_menu = True
            contin = True
        elif (self.rect.height >= 140) and (level == 5):
            winner = True

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def update_sprite(self):
        sprite_sheet = "run"
        if self.hit:
            sprite_sheet = "eat"
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
        self.sprite = pygame.transform.scale(self.sprite, (self.sprite.get_width()+self.radius, self.sprite.get_height()+self.radius))
        self.update()

    def update(self):
        self.animation_count += 1
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
        block = get_block(size, 96, 0)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def get_random_image(path):
    images = []
    for file in listdir(path):
        if file.endswith(".png"):
            images.append(join(path, file))
    return pygame.image.load(random.choice(images))


class Food(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, w, h, dir):
        self.type = dir.lower()
        super().__init__(x, y, w, h, self.type)
        self.image = pygame.transform.scale2x(get_random_image('assets/food/'+dir))
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0

    def loop(self):
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
        if self.animation_count // self.ANIMATION_DELAY > 10:
            self.animation_count = 0

    def update(self):
        self.kill()


def get_background(sprite):
    image = pygame.image.load(join("assets", "background", sprite))
    _, _, w, h = image.get_rect()
    tiles = []
    for i in range(WIDTH // w + 1):
        for j in range(HEIGHT // h + 1):
            pos = [i * w, j * h]
            tiles.append(pos)
    return tiles, image


def draw(window, background, bg_image, player, objects=None, offset_x=0):
    for tile in background:
        window.blit(bg_image, tuple(tile))
    for obj in objects:
        obj.draw(window, offset_x)
    player.draw(window, offset_x)
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

    if not collide_right:
        player.move_right(VELOCITY)
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)

    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "good":
            player.make_hit(obj, 'good')
            objects.remove(obj)
            break
        if obj and obj.name == "bad":
            player.make_hit(obj, 'bad')
            objects.remove(obj)
            break


def main(window):
    global main_menu, tutorial, game_over, winner, VELOCITY, GRAVITY, level, contin
    clock = pygame.time.Clock()
    background, bg_image = get_background("Yellow.png")

    block_size = 96
    hero = Hero(100,100, 50, 50)
    floor = []
    objects = []

    offset_x = 0
    scroll_area_width = 400

    start_button = Button(WIDTH - 200, 100, start_image)
    exit_button = Button(WIDTH - 200, 300, exit_image)
    tutorial_button = Button(WIDTH - 200, 200, tutorial_image)
    continue_button = Button(WIDTH - 200, 100, continue_image)
    restart_button = Button(WIDTH - 200, 100, restart_image)
    pygame.mixer.music.load('assets/music/funnysong.mp3')
    pygame.mixer.music.play(-1)

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
            font = pygame.font.Font('assets/fonts/Cooper Black Regular.ttf', 36)
            text = font.render("LEVEL "+str(level), True, (0, 0, 0))
            window.blit(text, (WIDTH - 190, text.get_height()- 10))

            if exit_button.draw():
                run = False
                break
            if tutorial_button.draw():
                main_menu = False
                tutorial = True
            if contin == False:
                if start_button.draw():
                    offset_x = 0
                    hero.rect.x = 0

                    food = [Food(i * 330, HEIGHT - block_size - 54, 38, 38, random.choice(["Good", "Bad"])) for i in
                                range(2, 70)]
                    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in
                                 range(-WIDTH // block_size, WIDTH * 40 // block_size)]

                    objects = [*floor, *food]
                    main_menu = False
            if contin:
                if continue_button.draw():
                    offset_x = 0
                    hero.kill()
                    hero = Hero(100, 100, 50, 50)
                    GRAVITY = 1
                    VELOCITY = 5
                    hero.rect.x = 0

                    food = [Food(i * 330, HEIGHT - block_size - 54, 38, 38, random.choice(["Good", "Bad"])) for i in
                            range(2, 70)]
                    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in
                             range(-WIDTH // block_size, WIDTH * 40 // block_size)]

                    objects = [*floor, *food]
                    main_menu = False
            pygame.display.update()
        elif tutorial == True and main_menu == False:
            window.blit(tutorial_background, (0, 0))
            if start_button.draw():
                offset_x = 0
                hero.rect.x = 0
                food = [Food(i * 330, HEIGHT - block_size - 54, 38, 38, random.choice(["Good", "Bad"])) for i in
                        range(2, 70)]
                floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in
                         range(-WIDTH // block_size, WIDTH * 30 // block_size)]
                objects = [*floor, *food]
                main_menu = False
                tutorial = False
            pygame.display.flip()
        elif game_over == True:
            window.blit(bkg_gameover, (0, 0))  # start menu bkgnd
            if restart_button.draw():
                main_menu = True
                game_over = False
                hero.kill()
                hero = Hero(100, 100, 50, 50)
                GRAVITY = 1
                VELOCITY = 5
            pygame.display.update()
        elif winner == True:
            window.blit(bkg_winner, (0, 0))  # start menu bkgnd
            if restart_button.draw():
                main_menu = True
                winner = False
                hero.kill()
                hero = Hero(100, 100, 50, 50)
                GRAVITY = 1
                VELOCITY = 5
                level = 1
                contin = False
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