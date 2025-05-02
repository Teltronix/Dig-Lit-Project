import pygame
import os
import subprocess
import sys

pygame.init()

# Dynamically construct the base path
base_path = os.path.dirname(__file__)

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Party Game")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
BLUE  = (0,   0, 255)
RED   = (255, 0,   0)
GREEN = (0, 255,   0)  # Portal

# Player setup
player_size  = 40
player_speed = 5
player = pygame.Rect(
    WIDTH//2 - player_size//2,
    HEIGHT//2 - player_size//2,
    player_size, player_size
)

# Sprite setup
sprite_size     = 50
sprite_positions = [
    (WIDTH//2 - sprite_size//2,    100),            # Top
    (WIDTH//2 - sprite_size//2,    HEIGHT - 150),   # Bottom
    (100,                          HEIGHT//2 - 25),  # Left
    (WIDTH - 150,                  HEIGHT//2 - 25),  # Right
    (150,                          150),             # Top-left
    (WIDTH - 200,                  HEIGHT - 200)     # Bottom-right
]
sprites = [pygame.Rect(x, y, sprite_size, sprite_size)
           for x, y in sprite_positions]

# Portal setup (hidden until all spoken)
portal_size   = 60
portal_rect   = pygame.Rect(
    WIDTH//2 - portal_size//2,
    HEIGHT//2 - portal_size//2,
    portal_size, portal_size
)
portal_active = False

# Track which sprites have spoken
spoken = [False] * len(sprites)

# Six text‐screens in fixed order
text_screens = [
    "You found the first clue!",
    "This is the second message.",
    "Third screen of text.",
    "Fourth message appears here.",
    "Fifth screen is displayed.",
    "Final message: You did it!"
]
text_index     = 0
showing_text   = False
last_collision = None

# Which file to launch next?
next_file = None

# Font
font = pygame.font.SysFont(None, 48)

running = True
while running:
    dt = clock.tick(60)

    # — Event handling —
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if showing_text and event.key == pygame.K_SPACE:
                showing_text = False
                text_index   = (text_index + 1) % len(text_screens)
            elif event.key == pygame.K_ESCAPE:
                running = False

    keys = pygame.key.get_pressed()

    # — Game logic —
    if not showing_text:
        # clear last_collision once stepped off
        if last_collision is not None and not player.colliderect(sprites[last_collision]):
            last_collision = None

        # movement
        if keys[pygame.K_LEFT]:
            player.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player.x += player_speed
        if keys[pygame.K_UP]:
            player.y -= player_speed
        if keys[pygame.K_DOWN]:
            player.y += player_speed

        # stay on screen
        player.x = max(0, min(player.x, WIDTH  - player_size))
        player.y = max(0, min(player.y, HEIGHT - player_size))

        # talk to sprites
        if last_collision is None:
            for idx, sprite in enumerate(sprites):
                if player.colliderect(sprite) and not spoken[idx]:
                    showing_text   = True
                    last_collision = idx
                    spoken[idx]    = True
                    break

        # activate portal when done
        if all(spoken):
            portal_active = True

        # if you step into the portal, plan to load the next world
        if portal_active and player.colliderect(portal_rect):
            next_file = "AfterPartyGame.py"
            running   = False

    # — Drawing —
    screen.fill(WHITE)

    if showing_text:
        surf = font.render(text_screens[text_index], True, BLACK)
        rect = surf.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(surf, rect)
    else:
        for sprite in sprites:
            pygame.draw.rect(screen, BLUE, sprite)
        pygame.draw.rect(screen, RED, player)
        if portal_active:
            pygame.draw.rect(screen, GREEN, portal_rect)

    pygame.display.flip()

pygame.quit()

# — Launch the next script using an absolute path —
if next_file:
    next_path = os.path.join(base_path, next_file)
    subprocess.Popen(["python3", next_path])
    sys.exit()