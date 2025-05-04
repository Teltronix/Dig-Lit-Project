import os
import sys
import subprocess
import pygame
import spritesheet

pygame.init()

# — paths & config —
base_path  = os.path.dirname(__file__)
image_path = os.path.join(base_path, 'Brain.png')

DOOR_IMAGES   = ['Green_Dungeon_Door.png', 'Pink_Dungeon_Door.png']
DOOR_SCRIPTS  = ['death area.py', 'CarGame.py']
DOOR_MESSAGES = [
    "The familiar beep comforts you",
    "The screeching intrigues you"
]
DOOR_SCALE = 5

# — screen & world —
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Brain Area")
clock = pygame.time.Clock()

WORLD_HEIGHT       = HEIGHT * 3
world_surface      = pygame.Surface((WIDTH, WORLD_HEIGHT))
camera_y           = 0
SCROLL_DOWN_THRESH = HEIGHT - 100
SCROLL_UP_THRESH   = 100

# — load & animate player sprite with transparency keyed out —
brain_img    = pygame.image.load(image_path).convert_alpha()
sprite_sheet = spritesheet.BrainSprite(brain_img)

animation_list = []
for i in range(5):
    frame_img = sprite_sheet.get_image(i, 32, 32, scale=10).convert_alpha()
    # treat black as transparent
    frame_img.set_colorkey((0, 0, 0))
    animation_list.append(frame_img)

player_rect    = animation_list[0].get_rect(center=(WIDTH // 2, 100))
frame          = 0
ANIM_COOLDOWN  = 125
last_anim_time = pygame.time.get_ticks()
speed          = 5

# — font & narrative text —
font = pygame.font.SysFont(None, 28)
story_lines = [
    "Nothingness, emptiness, silence. Yet I hear noises, oscillating through the air.",
    "A faint beep pierces the silence ever so often.",
    "Is it real? Am I real? Who am … no. What am I.",
    "Cold surrounds me but I feel warm. Something isn’t right.",
    "This feeling I can’t describe, but can I even feel?",
    "I don’t know what I am.",
    "",
    "There’s pressure in my chest, but no pain.",
    "Light flickers behind closed eyes, though I don’t remember closing them.",
    "Everything is weightless. Time doesn’t pass, but something is moving.",
    "",
    "Thoughts drift in and out like smoke.",
    "I try to hold onto one, but they vanish before I understand them.",
    "A name almost surfaces. It feels familiar. Then it’s gone.",
    "",
    "Sound. I hear? This time it’s different. Some kind of … screeching?",
    "Make it stop.",
    "Make it stop.",
    "Make it stop.",
    "Metal crumbling, a loud noise.",
    "A big pressure surrounds me, holding me in place",
    "…",
    "It’s gone.",
    "Wait, what’s gone?",
    "I can’t seem to remember.",
    "Oh.",
    "",
    "My body tenses. No… no, that wasn’t a memory. But was it? Memory? I can’t seem to remember.",
    "I can’t seem to remember?",
    "What is happening?",
    "",
    "The nothingness returned.",
    "The familiar beep pierces the air again.",
    "",
    "Two doors appear before you, which do you choose?"
]

current_line       = 0
current_text       = ""
char_index         = 0
TYPE_DELAY         = 30
PAUSE_DELAY        = 600
last_char_time     = pygame.time.get_ticks()
line_finished      = False
line_finish_time   = 0
displayed_lines    = []
story_finished     = False

# — load & position doors (extra 250px gap) —
door_images = []
door_rects  = []
margin = 600 + 250

# compute total width for centering
widths = []
for img_name in DOOR_IMAGES:
    tmp = pygame.image.load(os.path.join(base_path, img_name)).convert_alpha()
    w, _ = tmp.get_size()
    widths.append(w * DOOR_SCALE)
total_w = sum(widths) + margin * (len(widths) - 1)
start_x = (WIDTH - total_w) // 2
door_y   = HEIGHT * 2 + 100

x = start_x
for img_name in DOOR_IMAGES:
    img = pygame.image.load(os.path.join(base_path, img_name)).convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (w * DOOR_SCALE, h * DOOR_SCALE))
    door_images.append(img)
    rect = img.get_rect(midtop=(x + img.get_width() // 2, door_y))
    door_rects.append(rect)
    x += img.get_width() + margin

# — main loop —
running = True
while running:
    dt  = clock.tick(60)
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or \
           (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

        elif event.type == pygame.KEYDOWN:
            # skip / advance narrative
            if not story_finished and event.key == pygame.K_SPACE:
                if not line_finished:
                    current_text   = story_lines[current_line]
                    char_index     = len(current_text)
                    line_finished  = True
                    line_finish_time = now
                else:
                    displayed_lines.append(story_lines[current_line])
                    current_line += 1
                    if current_line >= len(story_lines):
                        story_finished = True
                    else:
                        current_text  = ""
                        char_index    = 0
                        line_finished = False
                continue

            # enter door after narrative
            if story_finished and event.key == pygame.K_SPACE:
                for idx, rect in enumerate(door_rects):
                    if player_rect.colliderect(rect):
                        pygame.quit()
                        subprocess.Popen([
                            sys.executable,
                            os.path.join(base_path, DOOR_SCRIPTS[idx])
                        ])
                        running = False
                        break
                continue

    # movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  player_rect.x -= speed
    if keys[pygame.K_RIGHT]: player_rect.x += speed
    if keys[pygame.K_UP]:    player_rect.y -= speed
    if keys[pygame.K_DOWN]:  player_rect.y += speed

    # animate player
    if now - last_anim_time >= ANIM_COOLDOWN:
        frame         = (frame + 1) % len(animation_list)
        last_anim_time = now

    # typewriter auto-advance
    if not story_finished and not line_finished:
        if char_index < len(story_lines[current_line]) and now - last_char_time > TYPE_DELAY:
            current_text   += story_lines[current_line][char_index]
            char_index     += 1
            last_char_time = now
        elif char_index >= len(story_lines[current_line]):
            line_finished    = True
            line_finish_time = now

    if line_finished and not story_finished and now - line_finish_time > PAUSE_DELAY:
        displayed_lines.append(story_lines[current_line])
        current_line += 1
        if current_line >= len(story_lines):
            story_finished = True
        else:
            current_text   = ""
            char_index     = 0
            line_finished  = False

    # camera follow up/down
    if player_rect.bottom > camera_y + SCROLL_DOWN_THRESH:
        camera_y = min(player_rect.bottom - SCROLL_DOWN_THRESH, WORLD_HEIGHT - HEIGHT)
    elif player_rect.top < camera_y + SCROLL_UP_THRESH:
        camera_y = max(player_rect.top - SCROLL_UP_THRESH, 0)

    # — draw world content —
    world_surface.fill((0, 0, 0))

    # draw past lines
    for i, line in enumerate(displayed_lines):
        surf = font.render(line, True, (255, 255, 255))
        world_surface.blit(surf, (20, 45 + 30 * i))

    # draw current typing line
    if not story_finished:
        surf = font.render(current_text, True, (255, 255, 255))
        world_surface.blit(surf, (20, 45 + 30 * len(displayed_lines)))

    # draw doors
    if story_finished:
        for img, rect in zip(door_images, door_rects):
            world_surface.blit(img, rect)

    # — blit world + player + UI —
    # world slice
    screen.blit(
        world_surface,
        (0, 0),
        area=pygame.Rect(0, camera_y, WIDTH, HEIGHT)
    )
    # player on top, with transparency
    screen.blit(
        animation_list[frame],
        (player_rect.x, player_rect.y - camera_y)
    )

    # instruction fixed on screen
    if story_finished:
        instr = font.render(
            "Walk into a door to see your choice, then press SPACE to enter",
            True, (255, 255, 255)
        )
        screen.blit(instr, (20, HEIGHT - 40))

        # draw choice box above door when in its hitbox
        for idx, rect in enumerate(door_rects):
            if player_rect.colliderect(rect):
                bw, bh = 300, 50
                bx = rect.centerx - bw // 2
                by = rect.top - bh - 10 - camera_y

                box = pygame.Surface((bw, bh), pygame.SRCALPHA)
                box.fill((0, 0, 0, 200))
                pygame.draw.rect(box, (255, 255, 255), (0, 0, bw, bh), 2)
                screen.blit(box, (bx, by))

                msg = font.render(DOOR_MESSAGES[idx], True, (255, 255, 255))
                mr  = msg.get_rect(center=(rect.centerx, by + bh // 2))
                screen.blit(msg, mr)

    pygame.display.flip()

pygame.quit()
sys.exit()