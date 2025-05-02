import os
import pygame
import spritesheet

pygame.init()

# Set up paths
base_path = os.path.dirname(__file__)
image_path = os.path.join(base_path, 'Brain.png')

# Set up screen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Brain Area")
clock = pygame.time.Clock()

# Load sprite
brain_sprite_image = pygame.image.load(image_path).convert_alpha()
sprite_sheet = spritesheet.BrainSprite(brain_sprite_image)
animation_list = [sprite_sheet.get_image(i, 32, 32, scale=10) for i in range(5)]

# Font setup
font = pygame.font.SysFont(None, 28)

# Narrative text
story_lines = [
    "There was a hallway I used to know.",
    "It smelled like dust and disinfectant. The lights hummed even when everything else stayed quiet.",
    "I don’t know where it led, but I walked it often. Maybe too often. Maybe not at all.",
    "Time doesn’t work here. I measure it in flickers. In loops. In the way my shadow moves even when I don’t.",
    "I see things sometimes. Not in the corner of my eye. I’m past that now.",
    "I see them in the middle. The direct gaze. The center of attention. And still, they don’t stay.",
    "There was a door once. I think I passed through it. Or maybe I stood outside it and forgot why I knocked.",
    "This place doesn’t hurt. That’s the strange part. It should. The silence should ache. The repetition should grind.",
    "But I feel nothing.",
    "Someone used to say my name. I don't know who. It echoes in shapes, not sound.",
    "I try to piece things together. I remember lights. Red, then white. Movement. Then none.",
    "I remember my chest rising. Then rising again. Too steady. Too regular.",
    "My hands don’t do what they should. I think I had hands. I think they were mine.",
    "I am not asleep. I am not awake.",
    "I am in between.",
    "And something is watching me wait."
]

# Typewriter effect setup
current_line = 0
current_text = ''
char_index = 0
type_delay = 30
last_char_time = pygame.time.get_ticks()
displayed_lines = []

# Player setup
player_rect = animation_list[0].get_rect(center=(WIDTH // 2, HEIGHT // 2))
frame = 0
animation_cooldown = 125
last_update = pygame.time.get_ticks()
speed = 5

# Game loop
running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE and char_index >= len(story_lines[current_line]):
                displayed_lines.append(story_lines[current_line])
                current_line += 1
                if current_line >= len(story_lines):
                    current_line = len(story_lines) - 1
                current_text = ''
                char_index = 0

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= speed
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
        player_rect.x += speed
    if keys[pygame.K_UP] and player_rect.top > 0:
        player_rect.y -= speed
    if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT:
        player_rect.y += speed

    current_time = pygame.time.get_ticks()
    if current_time - last_update >= animation_cooldown:
        frame = (frame + 1) % len(animation_list)
        last_update = current_time

    if char_index < len(story_lines[current_line]) and current_time - last_char_time > type_delay:
        current_text += story_lines[current_line][char_index]
        char_index += 1
        last_char_time = current_time

    screen.fill((0, 0, 0))
    screen.blit(animation_list[frame], player_rect)

    for i, line in enumerate(displayed_lines):
        line_surf = font.render(line, True, (255, 255, 255))
        screen.blit(line_surf, (20, 20 + i * 30))

    current_surf = font.render(current_text, True, (255, 255, 255))
    screen.blit(current_surf, (20, 20 + len(displayed_lines) * 30))

    pygame.display.flip()

pygame.quit()
