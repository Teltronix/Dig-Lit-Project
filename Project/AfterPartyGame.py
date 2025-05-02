import os
import pygame
import spritesheet

pygame.init()

# Dynamically construct the absolute path to Brain.png
base_path = os.path.dirname(__file__)  # Directory of the current script
image_path = os.path.join(base_path, 'Brain.png')

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Brain Area")
clock = pygame.time.Clock()

# Load the image using the dynamically constructed path
brain_sprite_image = pygame.image.load(image_path).convert_alpha()
sprite_sheet = spritesheet.BrainSprite(brain_sprite_image)
animation_list = [sprite_sheet.get_image(i, 32, 32, scale=10) for i in range(5)]

font = pygame.font.SysFont(None, 28)
text_lines = [
    "Welcome to the blank text world!",
    "You can walk through any 'letters' here.",
    "",
    "Use arrow keys to move around.",
    "Press ESC to quit."
]

player_rect = animation_list[0].get_rect(center=(WIDTH // 2, HEIGHT // 2))
frame = 0
animation_cooldown = 125
last_update = pygame.time.get_ticks()
speed = 5

running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0: player_rect.x -= speed
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH: player_rect.x += speed
    if keys[pygame.K_UP] and player_rect.top > 0: player_rect.y -= speed
    if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT: player_rect.y += speed
    if keys[pygame.K_ESCAPE]: running = False

    current_time = pygame.time.get_ticks()
    if current_time - last_update >= animation_cooldown:
        frame = (frame + 1) % len(animation_list)
        last_update = current_time

    screen.fill((0, 0, 0))
    for i, line in enumerate(text_lines):
        surf = font.render(line, True, (255, 255, 255))
        screen.blit(surf, (20, 20 + i * 30))
    screen.blit(animation_list[frame], player_rect)

    pygame.display.flip()

pygame.quit()