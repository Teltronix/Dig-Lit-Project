import os
import sys
import subprocess
import pygame
import spritesheet

pygame.init()

# Dynamically construct the base path
base_path = os.path.dirname(__file__)

# Door configuration
DOOR_IMAGES  = ['Green_Dungeon_Door.png', 'Pink_Dungeon_Door.png']
DOOR_SCRIPTS = ['death area.py', 'PartyGame.py']
DOOR_SCALE   = 5  # how much to enlarge the door PNGs

# Screen setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Ghost World")
clock = pygame.time.Clock()

# Load ghost sprite sheet
ghost_sprite_path = os.path.join(base_path, 'Ghost.png')
ghost_sprite_image = pygame.image.load(ghost_sprite_path).convert_alpha()
ghost_sheet = spritesheet.Ghost(ghost_sprite_image)
ghost_frames = [ghost_sheet.get_image(i, 32, 32, scale=9) for i in range(4)]
ghost_frame = 0
ghost_cooldown = 125
ghost_last_update = pygame.time.get_ticks()

# Ghost position & speed
ghost_rect = ghost_frames[0].get_rect(center=(WIDTH // 2, HEIGHT // 2))
ghost_speed = 4

# Font and floating text
font = pygame.font.SysFont(None, 32)
floating_text = [
    "The silence is loud here.",
    "Is this... the end?",
    "Or the beginning of something else?",
    "Move with arrow keys.",
    "Press ESC to quit."
]

# Load and scale door images
door_images = []
door_rects  = []
for img_name in DOOR_IMAGES:
    img_path = os.path.join(base_path, img_name)
    img = pygame.image.load(img_path).convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (w * DOOR_SCALE, h * DOOR_SCALE))
    door_images.append(img)

# Position doors with a fixed margin between them
if door_images:
    margin = 600  # ← pixels gap between the two doors; increase to push them further apart
    widths = [img.get_width() for img in door_images]
    total_w = sum(widths) + margin * (len(door_images) - 1)
    start_x = (WIDTH - total_w) // 2

    x = start_x
    for img in door_images:
        rect = img.get_rect(midbottom=(x + img.get_width() // 2, HEIGHT - 50))
        door_rects.append(rect)
        x += img.get_width() + margin

running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # If ghost stands on a door and you press SPACE, launch its script
            elif event.key == pygame.K_SPACE:
                for idx, rect in enumerate(door_rects):
                    if ghost_rect.colliderect(rect):
                        pygame.quit()
                        subprocess.Popen([
                            sys.executable,
                            os.path.join(base_path, DOOR_SCRIPTS[idx])
                        ])
                        running = False
                        break

    # Movement controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        ghost_rect.x -= ghost_speed
    if keys[pygame.K_RIGHT]:
        ghost_rect.x += ghost_speed
    if keys[pygame.K_UP]:
        ghost_rect.y -= ghost_speed
    if keys[pygame.K_DOWN]:
        ghost_rect.y += ghost_speed

    # Ghost animation update
    now = pygame.time.get_ticks()
    if now - ghost_last_update >= ghost_cooldown:
        ghost_frame = (ghost_frame + 1) % len(ghost_frames)
        ghost_last_update = now

    # DRAW
    screen.fill((0, 0, 0))

    # 1) draw doors behind the ghost
    for img, rect in zip(door_images, door_rects):
        screen.blit(img, rect)

    # 2) draw ghost on top
    screen.blit(ghost_frames[ghost_frame], ghost_rect)

    # 3) draw floating text
    for i, line in enumerate(floating_text):
        text_surface = font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (30, 30 + i * 30))

    pygame.display.flip()

pygame.quit()
sys.exit()