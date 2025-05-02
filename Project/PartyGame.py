import pygame
import os
import subprocess
import sys
import random
import string

pygame.init()

# Setup
base_path = os.path.dirname(__file__)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Party Game")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BOX_COLOR = (240, 240, 240)
BOX_BORDER = (50, 50, 50)

# Fonts
gaster_font = pygame.font.Font("wingdings.otf", 36)
normal_font = pygame.font.SysFont(None, 32)
hint_font = pygame.font.SysFont(None, 24)

# Cryptic name
cryptic_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

# Player setup
player_size = 40
player_speed = 5
player = pygame.Rect(WIDTH // 2 - player_size // 2, HEIGHT // 2 - player_size // 2, player_size, player_size)

# NPC Sprites
sprite_size = 50
sprite_positions = [
    (WIDTH // 2 - sprite_size // 2, 100),
    (WIDTH // 2 - sprite_size // 2, HEIGHT - 150),
    (100, HEIGHT // 2 - 25),
    (WIDTH - 150, HEIGHT // 2 - 25),
    (150, 150),
    (WIDTH - 200, HEIGHT - 200)
]
sprites = [pygame.Rect(x, y, sprite_size, sprite_size) for x, y in sprite_positions]

# Portal setup
portal_size = 60
portal_rect = pygame.Rect(WIDTH // 2 - portal_size // 2, HEIGHT // 2 - portal_size // 2, portal_size, portal_size)
portal_active = False
portal_entered = False

# Dialogue setup
text_screens = [
    "Heyyy... CRYPTIC_NAME, long time no see!",
    "You made it! Grab a drink, find a seat. Same ol’ you, huh?",
    "You ever wonder why the lights never turn off here?",
    "Funny thing is… you used to hate parties. Or did you forget that too?",
    "We’ve been here for weeks. Just... watching. Talking. You didn’t move. You didn’t blink. But we kept talking.",
    "You're not at a party. You're in a bed. Wires. Machines. A pulse. We’re all still here. Still hoping you hear us."
]
final_message = "But no one was there."

text_index = 0
showing_text = False
current_text = ""
text_npcs = []
final_message_played = False
npc_removed = False

next_file = "AfterPartyGame.py"

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    return lines

def draw_text_box(text):
    box_width, box_height = 700, 150
    box_rect = pygame.Rect(WIDTH // 2 - box_width // 2, HEIGHT // 2 - box_height // 2, box_width, box_height)
    pygame.draw.rect(screen, BOX_COLOR, box_rect)
    pygame.draw.rect(screen, BOX_BORDER, box_rect, 4)

    if "CRYPTIC_NAME" in text:
        parts = text.split("CRYPTIC_NAME")
        part1_surf = normal_font.render(parts[0], True, BLACK)
        name_surf = gaster_font.render(cryptic_name, True, BLACK)
        part2_surf = normal_font.render(parts[1], True, BLACK)

        # Position all three inline
        x = box_rect.left + 20
        y = box_rect.top + 40

        part1_rect = part1_surf.get_rect(topleft=(x, y))
        screen.blit(part1_surf, part1_rect)

        x += part1_rect.width + 10
        name_rect = name_surf.get_rect(topleft=(x, y))
        screen.blit(name_surf, name_rect)

        x += name_rect.width + 10
        part2_rect = part2_surf.get_rect(topleft=(x, y))
        screen.blit(part2_surf, part2_rect)
    else:
        wrapped_lines = wrap_text(text, normal_font, box_width - 40)
        for i, line in enumerate(wrapped_lines):
            line_surf = normal_font.render(line, True, BLACK)
            line_rect = line_surf.get_rect(center=(box_rect.centerx, box_rect.top + 30 + i * 30))
            screen.blit(line_surf, line_rect)

    hint_surf = hint_font.render("Space to continue...", True, (80, 80, 80))
    hint_rect = hint_surf.get_rect(center=(box_rect.centerx, box_rect.bottom - 20))
    screen.blit(hint_surf, hint_rect)

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

            if showing_text and event.key == pygame.K_SPACE:
                # Show final message
                if text_index == len(text_screens) and not final_message_played:
                    current_text = final_message
                    final_message_played = True
                    showing_text = True

                # Remove all NPCs after final message
                elif final_message_played and not npc_removed:
                    sprites.clear()
                    npc_removed = True
                    portal_active = True  # ← activate portal here
                    showing_text = False


                else:
                    showing_text = False

    # Movement
    keys = pygame.key.get_pressed()
    if not showing_text:
        if keys[pygame.K_LEFT]: player.x -= player_speed
        if keys[pygame.K_RIGHT]: player.x += player_speed
        if keys[pygame.K_UP]: player.y -= player_speed
        if keys[pygame.K_DOWN]: player.y += player_speed
        player.clamp_ip(screen.get_rect())

        for sprite in sprites:
            if player.colliderect(sprite) and sprite not in text_npcs:
                if text_index < len(text_screens):
                    current_text = text_screens[text_index]
                    text_npcs.append(sprite)
                    text_index += 1
                    showing_text = True
                break

        if portal_active and player.colliderect(portal_rect):
            portal_entered = True
            running = False

    # Draw everything
    screen.fill(WHITE)
    for sprite in sprites:
        pygame.draw.rect(screen, BLUE, sprite)
    pygame.draw.rect(screen, RED, player)
    if portal_active:
        pygame.draw.rect(screen, GREEN, portal_rect)
    if showing_text:
        draw_text_box(current_text)

    pygame.display.flip()

pygame.quit()

# Launch next scene
if portal_entered:
    next_path = os.path.join(base_path, next_file)
    subprocess.Popen(["python3", next_path])
    sys.exit()
