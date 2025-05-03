import os
import pygame
import spritesheet

pygame.init()

# Setup
base_path = os.path.dirname(__file__)
image_path = os.path.join(base_path, 'Person.png')

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("????")
clock = pygame.time.Clock()

# Load sprite
person_sprite_image = pygame.image.load(image_path).convert_alpha()
sprite_sheet = spritesheet.playerv1(person_sprite_image)
animation_list = [sprite_sheet.get_image(i, 200, 600, scale=0.75) for i in range(30)]

# Font + text
font = pygame.font.SysFont(None, 28)
text_lines = [
    "Welcome to the blank text world!",
    "You can walk through any 'letters' here.",
    "",
    "Use arrow keys to move around.",
    "Press ESC to quit."
]

# Player setup
player_rect = animation_list[0].get_rect(center=(WIDTH // 2, HEIGHT // 2))
frame_index = 0
animation_cooldown = 50
last_update = pygame.time.get_ticks()
speed = 3
flipped = False
moving = False

# Main loop
running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    moving = False

    # Movement logic
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        dx = -speed
        flipped = True
        moving = True
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
        dx = speed
        flipped = False
        moving = True
    if keys[pygame.K_UP] and player_rect.top > 0:
        dy = -speed
        moving = True
    if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT:
        dy = speed
        moving = True
    if keys[pygame.K_ESCAPE]:
        running = False

    player_rect.x += dx
    player_rect.y += dy

    # Animation update
    current_time = pygame.time.get_ticks()
    if moving:
        if current_time - last_update >= animation_cooldown:
            frame_index = (frame_index + 1) % len(animation_list)
            last_update = current_time
    else:
        frame_index = 0  # idle frame

    # Draw everything
    screen.fill((0, 0, 0))
    for i, line in enumerate(text_lines):
        surf = font.render(line, True, (255, 255, 255))
        screen.blit(surf, (20, 20 + i * 30))

    sprite = animation_list[frame_index]
    if flipped:
        sprite = pygame.transform.flip(sprite, True, False)
    screen.blit(sprite, player_rect)

    pygame.display.flip()

pygame.quit()
