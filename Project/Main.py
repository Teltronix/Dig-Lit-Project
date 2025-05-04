import pygame
import spritesheet
import subprocess
import os

pygame.init()

# Dynamically construct the base path
base_path = os.path.dirname(__file__)

TILE_SIZE = 40
MAZE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,1],
    [1,1,0,1,0,1,0,1,1,0,1,0,1,1,0,1,1],
    [1,1,0,1,0,0,0,0,1,0,0,0,1,0,0,1,1],
    [1,1,0,1,1,1,1,0,1,1,1,0,1,0,1,1,1],
    [1,1,0,0,0,0,1,0,0,0,1,0,1,0,0,1,1],
    [1,1,1,1,1,0,1,1,1,0,1,0,1,1,0,1,1],
    [1,1,0,0,1,0,0,0,1,0,1,0,0,0,0,1,1],
    [1,1,0,1,1,1,1,0,1,1,1,1,1,1,0,1,1],
    [1,1,0,0,0,0,1,0,0,0,0,0,0,1,0,1,1],
    [1,1,1,1,1,0,1,1,1,1,1,1,0,1,0,1,1],
    [0,0,0,1,1,0,0,0,0,0,0,1,0,1,0,1,1],
    [1,1,0,1,1,1,1,1,1,1,0,1,1,1,0,1,1],
    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

FAKE_WALLS = {(1, 2), (0,2)}
EXIT_POS = (0, 2)
WIN_POS = (0, 12)

MAZE_WIDTH = len(MAZE[0]) * TILE_SIZE
MAZE_HEIGHT = len(MAZE) * TILE_SIZE
screen = pygame.display.set_mode((MAZE_WIDTH, MAZE_HEIGHT))

# Load Brain.png using an absolute path
brain_image_path = os.path.join(base_path, 'Brain.png')
brain_sprite_image = pygame.image.load(brain_image_path).convert_alpha()
sprite_sheet = spritesheet.BrainSprite(brain_sprite_image)
animation_list = [sprite_sheet.get_image(i, 32, 32, scale=10) for i in range(5)]

frame = 0
animation_cooldown = 125
last_update = pygame.time.get_ticks()

player_x, player_y = 2, 2
clock = pygame.time.Clock()
running = True

while running:
    clock.tick(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    new_x, new_y = player_x, player_y
    if keys[pygame.K_LEFT]: new_x -= 1
    if keys[pygame.K_RIGHT]: new_x += 1
    if keys[pygame.K_UP]: new_y -= 1
    if keys[pygame.K_DOWN]: new_y += 1
    if keys[pygame.K_ESCAPE]: running = False

    if 0 <= new_x < len(MAZE[0]) and 0 <= new_y < len(MAZE):
        if MAZE[new_y][new_x] == 0 or (new_x, new_y) in FAKE_WALLS:
            player_x, player_y = new_x, new_y

    if (player_x, player_y) == EXIT_POS:
        pygame.quit()
        # Dynamically construct the absolute path for brain_area.py
        brain_area_path = os.path.join(base_path, 'BrainArea.py')
        subprocess.Popen(["python3", brain_area_path])
        exit()
    
    if (player_x, player_y) == WIN_POS:
        pygame.quit()
        # Dynamically construct the absolute path for win area.py
        win_area_path = os.path.join(base_path, 'WinArea.py')
        subprocess.Popen(["python3", win_area_path])
        exit()

    screen.fill((0, 0, 0))
    for y, row in enumerate(MAZE):
        for x, tile in enumerate(row):
            if tile == 1 or (x, y) in FAKE_WALLS:
                pygame.draw.rect(screen, (255, 255, 255), (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    pygame.draw.circle(
        screen,
        (255, 0, 0),
        (player_x * TILE_SIZE + TILE_SIZE // 2, player_y * TILE_SIZE + TILE_SIZE // 2),
        TILE_SIZE // 3
    )

    current_time = pygame.time.get_ticks()
    if current_time - last_update >= animation_cooldown:
        frame = (frame + 1) % len(animation_list)
        last_update = current_time

    pygame.display.flip()

pygame.quit()