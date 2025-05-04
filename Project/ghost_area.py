import os
import sys
import subprocess
import pygame
import spritesheet

pygame.init()

# — paths & config —
base_path  = os.path.dirname(__file__)
ghost_sprite_path = os.path.join(base_path, 'Ghost.png')

DOOR_IMAGES   = ['Green_Dungeon_Door.png', 'Pink_Dungeon_Door.png']
DOOR_SCRIPTS  = ['PartyGame.py', 'death area.py']
DOOR_MESSAGES = [
    "Bright lights and music fill the room",
    "The whirring and beeping drag you in"
]
DOOR_SCALE    = 5

# — screen & world —
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT     = screen.get_size()
pygame.display.set_caption("Ghost World")
clock             = pygame.time.Clock()

WORLD_HEIGHT       = HEIGHT * 4
world_surface      = pygame.Surface((WIDTH, WORLD_HEIGHT))
camera_y           = 0
SCROLL_DOWN_THRESH = HEIGHT - 100
SCROLL_UP_THRESH   = 100

# — load & animate ghost sprite with transparency keyed out —
ghost_image    = pygame.image.load(ghost_sprite_path).convert_alpha()
ghost_sheet    = spritesheet.Ghost(ghost_image)
ghost_frames   = []
for i in range(4):
    f = ghost_sheet.get_image(i, 32, 32, scale=9).convert_alpha()
    f.set_colorkey((0, 0, 0))
    ghost_frames.append(f)
ghost_frame       = 0
GHOST_COOLDOWN    = 125
ghost_last_update = pygame.time.get_ticks()

ghost_rect  = ghost_frames[0].get_rect(center=(WIDTH//2, 100))
ghost_speed = 4

# — font & narrative text (with “…” lines included) —
font = pygame.font.SysFont(None, 32)
story_lines = [
    "The darkness is back.",
    "I can’t see around me. What is sight?",
    "I feel conflicted. My memory doesn’t quite work. Why was there a car?",
    "Car? What’s a car?",
    "",
    "I don’t know.",
    "I don’t know?",
    "I know?",
    "",
    "Quiet. Where am I? What am I?",
    "I’m aware of my presence, but I can’t quite tell what I am.",
    "What do I look like?",
    "",
    "…",
    "",
    "I hear something. Hear? Sound? I’m not really sure.",
    "No matter how far I go, I can’t quite reach it.",
    "Can I move? I try. Did I move? I can’t tell.",
    "The sound still lingers in the distance.",
    "Tantalizing.",
    "",
    "Something floats into my soul. A stream of gentle notes, almost soothing.",
    "Where is it? What is it?",
    "I hear something else. Laughter? I can’t quite tell. Whispers flood my body.",
    "I have a body? No, not quite.",
    "",
    "I feel warm, a sense of nostalgia. Something familiar is tugging at me.",
    "Why can’t I see?",
    "Something is out there.",
    "Why can’t I see?",
    "Why can’t I see?",
    "",
    "…",
    "",
    "The rhythmic pulse returns.",
    "Beep. Beep. Beep.",
    "Each pulse anchors me, but I feel free.",
    "I can feel. What am I?",
    "Why can’t I see?",
    "Why can’t I see?",
    "I can.",
    "",
    "…",
    "",
    "A sudden image floods my brain.",
    "Bright lights everywhere, nearly disorienting. Shadows are moving all around.",
    "Colors swirling, creating a pull sucking me in. I see blurred faces. Where am I?",
    "Lips are forming small, serene shapes.",
    "A Smile? Whose is it? Is it mine?",
    "",

    "I can’t remember.",
    "I can’t remember.",
    "I can’t remember.",
    "",
    "I can’t see.",
    "Come back.",
    "",

    "Something returns. A sensation? I don’t know what it is.",
    "Why is it familiar? Who am I?",
    "Clean. Sterile.",
    "",
    "…",
    "",
    "The murmurs grow clearer. A melody flows through me. It sounds pleasant.",
    "I can hear?",
    "A thumping bass pierces the calmness.",
    "Voices.",
    "Laughing?",
    "",
    "Why does it feel familiar?",
    "Why is it so familiar?",
    "WHY IS IT SO",
    "",
    "…",
    "", 
    "Then silence again.",
    "The echoes fade. Quiet returns, but something lingers.",
    "Something important, just beyond reach.",
    "I can’t reach. I try to move.",
    "",
    "I try to remember. I try to think. Nothing.",
    "Only this stupid machinery whirring. I can’t take it.",
    "",
    "...",
    "",
    "Wait.",
    "Machinery?",
    "Beep. Beep. Beep.",
    "",

    "A single word surfaces",
    "Party.",
    "Party? What is this word? It’s reassuring, yet I dread it.",
    "",

    "Pressure gently surrounds me again, comfortingly firm.",
    "I'm held. Safe? Restrained?",
    "I can't be sure.",
    "",
    "The beeping steadies my mind.",
    "I drift again, floating back into gentle nothingness.",
    "Waiting. Wondering.",
    "Who am I?",
    "Or better yet …",
    "Where am I?",
]


# — typewriter state —
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
widths = []
for img_name in DOOR_IMAGES:
    tmp = pygame.image.load(os.path.join(base_path, img_name)).convert_alpha()
    w, _ = tmp.get_size()
    widths.append(w * DOOR_SCALE)
total_w = sum(widths) + margin * (len(widths) - 1)
start_x = (WIDTH - total_w) // 2
door_y   = WORLD_HEIGHT - HEIGHT // 2  # half-screen above bottom

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
            # skip/advance typewriter
            if not story_finished and event.key == pygame.K_SPACE:
                if not line_finished:
                    current_text     = story_lines[current_line]
                    char_index       = len(current_text)
                    line_finished    = True
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

            # enter door after story
            if story_finished and event.key == pygame.K_SPACE:
                for idx, rect in enumerate(door_rects):
                    if ghost_rect.colliderect(rect):
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
    if keys[pygame.K_LEFT]:
        ghost_rect.x -= ghost_speed
    if keys[pygame.K_RIGHT]:
        ghost_rect.x += ghost_speed
    if keys[pygame.K_UP]:
        ghost_rect.y -= ghost_speed
    if keys[pygame.K_DOWN]:
        ghost_rect.y += ghost_speed

    # animate ghost
    if now - ghost_last_update >= GHOST_COOLDOWN:
        ghost_frame       = (ghost_frame + 1) % len(ghost_frames)
        ghost_last_update = now

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
            current_text  = ""
            char_index    = 0
            line_finished = False

    # camera follow up/down
    if ghost_rect.bottom > camera_y + SCROLL_DOWN_THRESH:
        camera_y = min(ghost_rect.bottom - SCROLL_DOWN_THRESH, WORLD_HEIGHT - HEIGHT)
    elif ghost_rect.top < camera_y + SCROLL_UP_THRESH:
        camera_y = max(ghost_rect.top - SCROLL_UP_THRESH, 0)

    # — draw world content —
    world_surface.fill((0, 0, 0))
    for i, line in enumerate(displayed_lines):
        surf = font.render(line, True, (255,255,255))
        world_surface.blit(surf, (20, 45 + 30 * i))

    if not story_finished:
        surf = font.render(current_text, True, (255,255,255))
        world_surface.blit(surf, (20, 45 + 30 * len(displayed_lines)))

    if story_finished:
        for img, rect in zip(door_images, door_rects):
            world_surface.blit(img, rect)

    # — blit world + ghost + UI —
    screen.blit(
        world_surface,
        (0, 0),
        area=pygame.Rect(0, camera_y, WIDTH, HEIGHT)
    )
    screen.blit(
        ghost_frames[ghost_frame],
        (ghost_rect.x, ghost_rect.y - camera_y)
    )

    if story_finished:
        instr = font.render(
            "Walk into a door to see your choice, then press SPACE to enter",
            True, (255,255,255)
        )
        screen.blit(instr, (20, HEIGHT - 40))

        # bigger choice box (400×80)
        for idx, rect in enumerate(door_rects):
            if ghost_rect.colliderect(rect):
                bw, bh = 400, 80
                bx = rect.centerx - bw // 2
                by = rect.top - bh - 10 - camera_y

                box = pygame.Surface((bw, bh), pygame.SRCALPHA)
                box.fill((0,0,0,200))
                pygame.draw.rect(box, (255,255,255), (0,0,bw,bh), 2)
                screen.blit(box, (bx, by))

                msg = font.render(DOOR_MESSAGES[idx], True, (255,255,255))
                mr  = msg.get_rect(center=(rect.centerx, by + bh//2))
                screen.blit(msg, mr)

    pygame.display.flip()

pygame.quit()
sys.exit()