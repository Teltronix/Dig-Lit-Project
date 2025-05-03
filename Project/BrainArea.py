import os
import sys
import subprocess
import pygame
import spritesheet

pygame.init()

# Set up paths
base_path = os.path.dirname(__file__)
image_path = os.path.join(base_path, 'Brain.png')

# Door config
DOOR_IMAGES   = ['Green_Dungeon_Door.png', 'Pink_Dungeon_Door.png']
DOOR_SCRIPTS  = ['death area.py', 'CarGame.py']
DOOR_SCALE    = 5   # scale doors by this factor

# Screen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Brain Area")
clock = pygame.time.Clock()

# Player animation
brain_sprite_image = pygame.image.load(image_path).convert_alpha()
sprite_sheet       = spritesheet.BrainSprite(brain_sprite_image)
animation_list     = [sprite_sheet.get_image(i, 32, 32, scale=10) for i in range(5)]

# Font
font = pygame.font.SysFont(None, 28)

# Narrative text
story_lines = [
    "There was a hallway I used to know.",
    "It smelled like dust and disinfectant. The lights hummed even when everything else stayed quiet.",
    # … rest of your lines …
    "And something is watching me wait."
]

# Typewriter state
current_line       = 0
current_text       = ''
char_index         = 0
type_delay         = 30
pause_delay        = 1000
last_char_time     = pygame.time.get_ticks()
line_finished      = False
line_finished_time = 0
displayed_lines    = []
story_finished     = False

# Player
player_rect    = animation_list[0].get_rect(center=(WIDTH//2, HEIGHT//2))
frame          = 0
anim_cooldown  = 125
last_update    = pygame.time.get_ticks()
speed          = 5

# Load & scale doors
door_images = []
door_rects  = []
for img_name in DOOR_IMAGES:
    img = pygame.image.load(os.path.join(base_path, img_name)).convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (w * DOOR_SCALE, h * DOOR_SCALE))
    door_images.append(img)

# Position doors with a fixed margin between them
if door_images:
    margin = 600  # pixels between each door
    widths = [img.get_width() for img in door_images]
    total_w = sum(widths) + margin * (len(door_images) - 1)
    start_x = (WIDTH - total_w) // 2

    x = start_x
    for img in door_images:
        rect = img.get_rect(midbottom=(x + img.get_width()//2, HEIGHT - 50))
        door_rects.append(rect)
        x += img.get_width() + margin

# Main loop
running = True
while running:
    dt  = clock.tick(60)
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif story_finished and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # Launch door script if standing on it
            for idx, rect in enumerate(door_rects):
                if player_rect.colliderect(rect):
                    pygame.quit()
                    subprocess.Popen([sys.executable,
                                      os.path.join(base_path, DOOR_SCRIPTS[idx])])
                    running = False
                    break

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]  and player_rect.left > 0:      player_rect.x -= speed
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH: player_rect.x += speed
    if keys[pygame.K_UP]    and player_rect.top > 0:       player_rect.y -= speed
    if keys[pygame.K_DOWN]  and player_rect.bottom < HEIGHT: player_rect.y += speed

    # Animate player
    if now - last_update >= anim_cooldown:
        frame = (frame + 1) % len(animation_list)
        last_update = now

    # Typewriter
    if not story_finished and not line_finished:
        if char_index < len(story_lines[current_line]) and now - last_char_time > type_delay:
            current_text += story_lines[current_line][char_index]
            char_index += 1
            last_char_time = now
        elif char_index >= len(story_lines[current_line]):
            line_finished      = True
            line_finished_time = now

    # After pause, lock in line & advance
    if line_finished and not story_finished and now - line_finished_time > pause_delay:
        displayed_lines.append(story_lines[current_line])
        current_line += 1
        if current_line >= len(story_lines):
            story_finished = True
        else:
            current_text  = ''
            char_index    = 0
            line_finished = False

    # --- DRAW ---
    screen.fill((0,0,0))

    # 1) draw all past lines
    for i, line in enumerate(displayed_lines):
        surf = font.render(line, True, (255,255,255))
        screen.blit(surf, (20, 20 + 30*i))

    # 2) draw current typing line
    if not story_finished:
        surf = font.render(current_text, True, (255,255,255))
        screen.blit(surf, (20, 20 + 30*len(displayed_lines)))

    # 3) once done, draw doors behind the player
    if story_finished:
        for img, rect in zip(door_images, door_rects):
            screen.blit(img, rect)
        instr = font.render("Walk to a door and press SPACE to enter", True, (255,255,255))
        screen.blit(instr, (20, HEIGHT-40))

    # 4) draw player on top
    screen.blit(animation_list[frame], player_rect)

    pygame.display.flip()

pygame.quit()