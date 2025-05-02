import os
import sys
import subprocess
import pygame
import spritesheet

pygame.init()

# Dynamically construct the absolute path to your assets
base_path = os.path.dirname(__file__)
image_path = os.path.join(base_path, 'Person.png')

# Door configuration
DOOR_IMAGES  = ['Green_Dungeon_Door.png', 'Pink_Dungeon_Door.png']
DOOR_SCRIPTS = ['death area.py', 'HospitalGame.py']
DOOR_SCALE   = 5  # scale factor for door images

# Screen setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Blank Text World")
clock = pygame.time.Clock()

# Load and prepare player sprite animation
person_sprite_image = pygame.image.load(image_path).convert_alpha()
sprite_sheet = spritesheet.playerv1(person_sprite_image)
animation_list = [sprite_sheet.get_image(i, 32, 32, scale=10) for i in range(4)]
player_rect = animation_list[0].get_rect(center=(WIDTH//2, HEIGHT//2))
frame = 0
animation_cooldown = 125
last_update = pygame.time.get_ticks()
speed = 5

# Load & scale door images
door_images = []
door_rects  = []
for img_name in DOOR_IMAGES:
    img = pygame.image.load(os.path.join(base_path, img_name)).convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (w * DOOR_SCALE, h * DOOR_SCALE))
    door_images.append(img)

# Position doors with a fixed margin between them
if door_images:
    margin = 600  # pixels gap between the two doors; increase to push them further apart
    widths = [img.get_width() for img in door_images]
    total_w = sum(widths) + margin * (len(door_images) - 1)
    start_x = (WIDTH - total_w) // 2

    x = start_x
    for img in door_images:
        rect = img.get_rect(midbottom=(x + img.get_width()//2, HEIGHT - 50))
        door_rects.append(rect)
        x += img.get_width() + margin

# Text lines
font = pygame.font.SysFont(None, 28)
text_lines = [
    "Welcome to the blank text world!",
    "You can walk through any 'letters' here.",
    "",
    "Use arrow keys to move around.",
    "Press ESC to quit."
]

running = True
while running:
    dt = clock.tick(60)
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # If player overlaps a door and presses SPACE, launch its script
            elif event.key == pygame.K_SPACE:
                for idx, rect in enumerate(door_rects):
                    if player_rect.colliderect(rect):
                        pygame.quit()
                        subprocess.Popen([
                            sys.executable,
                            os.path.join(base_path, DOOR_SCRIPTS[idx])
                        ])
                        running = False
                        break

    # Movement controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= speed
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
        player_rect.x += speed
    if keys[pygame.K_UP] and player_rect.top > 0:
        player_rect.y -= speed
    if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT:
        player_rect.y += speed

    # Animate player
    if now - last_update >= animation_cooldown:
        frame = (frame + 1) % len(animation_list)
        last_update = now

    # DRAW
    screen.fill((0, 0, 0))

    # 1) Draw text
    for i, line in enumerate(text_lines):
        surf = font.render(line, True, (255, 255, 255))
        screen.blit(surf, (20, 20 + i * 30))

    # 2) Draw doors behind player
    for img, rect in zip(door_images, door_rects):
        screen.blit(img, rect)

    # 3) Draw player on top
    screen.blit(animation_list[frame], player_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()