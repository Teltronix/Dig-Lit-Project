import pygame
import sys
import os
import random
import spritesheet
import subprocess

pygame.init()

next_file = None

# Screen setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Midnight Motorist Style")
clock = pygame.time.Clock()

# Load sprite sheets and images
car_sprite_image = pygame.image.load('Car.png').convert_alpha()
tree_original = pygame.image.load('Tree.png').convert_alpha()
enemy_car_image = pygame.image.load('rac.png').convert_alpha()

# Resize tree to 32px wide and maintain aspect ratio
aspect_ratio = tree_original.get_height() / tree_original.get_width()
tree_width = 60
tree_height = int(tree_width * aspect_ratio)
tree_image = pygame.transform.scale(tree_original, (tree_width, tree_height))

# Sprite sheets
car_sheet = spritesheet.Car(car_sprite_image)

# Car animation setup
car_frames = [car_sheet.get_image(i, 32, 32, scale=8) for i in range(5)]
player_car_image = car_frames[0]
player_car_rect = player_car_image.get_rect(midleft=(100, HEIGHT // 2))
player_mask = pygame.mask.from_surface(player_car_image)

frame = 0
animation_cooldown = 1000
last_update = pygame.time.get_ticks()
crashing = False

# Bleed animation
bleed_frames = [car_sheet.get_image(i, 32, 32, scale=15) for i in range(5)]
bleed_frame = 0
bleeding = False
bleed_last_update = pygame.time.get_ticks()

# Road
road_img = pygame.image.load("road.png").convert()
road_img = pygame.transform.scale(road_img, (WIDTH, HEIGHT))
road_x = 0
scroll_speed = 10
scroll_count = 0

# Tree
tree_rect = pygame.Rect(WIDTH + 300, 20, tree_width, tree_height)

# Enemy cars (now include masks)
enemy_cars = []
for i, offset in enumerate([300, 600, 900]):
    car_img = pygame.transform.scale(enemy_car_image, (32 * 8, 32 * 8))
    random_y = random.randint(75, HEIGHT - 300)
    rect = car_img.get_rect(topleft=(WIDTH + offset, random_y))
    mask = pygame.mask.from_surface(car_img)
    enemy_cars.append((car_img, rect, mask))

# Game states
IN_RACING = 0
IN_BLEEDING = 2
state = IN_RACING

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def draw_racing_area():
    global road_x, scroll_count
    road_x -= scroll_speed
    if road_x <= -WIDTH:
        road_x = 0
        scroll_count += 1

    screen.blit(road_img, (road_x, 0))
    screen.blit(road_img, (road_x + WIDTH, 0))
    screen.blit(player_car_image, player_car_rect)

    # Enemy cars
    for car_img, car_rect, _ in enemy_cars:
        car_rect.x -= scroll_speed
        if car_rect.x < -100:
            car_rect.x = WIDTH + 300
            car_rect.y = random.randint(50, HEIGHT - 100)
        screen.blit(car_img, car_rect)

    # Tree
    if scroll_count >= 2:
        tree_rect.x -= scroll_speed
        screen.blit(tree_image, tree_rect)

def draw_bleeding_animation():
    global bleed_frame, bleed_last_update, bleeding
    now = pygame.time.get_ticks()
    if now - bleed_last_update >= animation_cooldown:
        bleed_last_update = now
        bleed_frame += 1
        global next_file, running
        if bleed_frame >= len(bleed_frames):
            bleeding = False
            next_file = "Maze.py"
            running = False

    screen.fill(WHITE)
    bleed_img = bleed_frames[min(bleed_frame, len(bleed_frames) - 1)]
    bleed_rect = bleed_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(bleed_img, bleed_rect)

# Main loop
running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if state == IN_RACING:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_car_rect.y -= 6
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_car_rect.y += 6
        player_car_rect.y = max(0, min(player_car_rect.y, HEIGHT - player_car_rect.height))

        # Update player mask position
        for _, car_rect, car_mask in enemy_cars:
            offset = (car_rect.x - player_car_rect.x, car_rect.y - player_car_rect.y)
            if player_mask.overlap(car_mask, offset):
                bleeding = True
                bleed_frame = 0
                bleed_last_update = pygame.time.get_ticks()
                state = IN_BLEEDING

        # Check tree collision with rectangle
        if scroll_count >= 2 and player_car_rect.colliderect(tree_rect):
            next_file = "ghost_area.py"
            running = False

        # Animate
        player_car_image = car_frames[0]
        player_mask = pygame.mask.from_surface(player_car_image)  # Refresh mask if animated
        draw_racing_area()

    elif state == IN_BLEEDING:
        draw_bleeding_animation()

    pygame.display.flip()

pygame.quit()

if next_file:
    subprocess.Popen(["python3", next_file])

sys.exit()
