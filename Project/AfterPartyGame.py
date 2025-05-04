import os
import sys
import subprocess
import pygame
import spritesheet

pygame.init()

# — paths & config —
try:
    base_path = os.path.dirname(os.path.abspath(__file__))
except NameError:
    base_path = os.getcwd()

# Helper to load images
def load_image(name):
    p = os.path.join(base_path, name)
    if not os.path.exists(p):
        raise FileNotFoundError(f"Missing asset: {p}")
    return pygame.image.load(p).convert_alpha()

# — portal animator class —
class Portal:
    def __init__(self, sheet):
        self.sheet = sheet

    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), (frame * width, 0, width, height))
        if scale != 1:
            image = pygame.transform.scale(
                image,
                (int(width * scale), int(height * scale))
            )
        return image

# Screen & world
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
clock = pygame.time.Clock()
pygame.display.set_caption("Blank Text World")

WORLD_HEIGHT       = HEIGHT * 3.5
world_surface      = pygame.Surface((WIDTH, WORLD_HEIGHT))
camera_y           = 0
SCROLL_DOWN_THRESH = HEIGHT - 100
SCROLL_UP_THRESH   = 100

# — load & animate player sprite frames —
sheet = load_image('Person.png')
player_ss = spritesheet.playerv1(sheet)
animation_list = [
    player_ss.get_image(i, 200, 600, scale=0.6).convert_alpha()
    for i in range(30)
]
for img in animation_list:
    img.set_colorkey((0,0,0))

player_rect    = animation_list[0].get_rect(center=(WIDTH//2, 100))
frame          = 0
ANIM_COOLDOWN  = 65
last_anim_time = pygame.time.get_ticks()
speed          = 3
facing_left    = False

# — load & animate portal sprite sheet —
portal_sheet_img = load_image('portal.png')
portal_animator  = Portal(portal_sheet_img)
frame_count      = portal_sheet_img.get_width() // 498
portal_frames    = [
    portal_animator.get_image(i, 498, 498, 0.65)
    for i in range(frame_count)
]
portal_frame        = 0
PORTAL_COOLDOWN     = 125
last_portal_update  = pygame.time.get_ticks()

# position portal half a screen above the bottom of the world
portal_rect = portal_frames[0].get_rect(
    midtop=(WIDTH//2, WORLD_HEIGHT - HEIGHT//2)
)

# Confirmation popup state
show_confirm = False

# — typewriter text setup —
font = pygame.font.SysFont(None, 28)
font2 = pygame.font.SysFont(None, 18)
story_lines = [
    "I enter the darkness again, but it’s no longer dark. There’s these images all around me.",
    "Memories? I can’t tell whose they are. Mine?",
    "I don’t know.",
    "",
    "...",
    "",
    "The music and lights still affect me. I barely feel conscious. Conscious? Where am I?",
    "No, this isn’t right. Everything is blurry. Faint shadows are above me. A bright light shines down in my face, I can’t see.",
    "",
    "...",
    "",
    "Now it’s dark. Or was it always?",
    "I can move, but I can’t move. Where am I?",
    "Voices. I hear voices.",
    "",
    "...",
    "",
    "My name? What is my name. It’s there, on the tip of my tongue. Tongue?",
    "I feel my hands, my arms, my legs. Why can’t I move?",
    "",
    "...",
    "",
    "What happened?",
    "Party. The party. What happened?",
    "I CAN REMEMBER.",
    "",
    "...",
    "",
    "The voices and laughter are clear now. They are familiar. Her voice. Her laugh.",
    "Why does it hurt? What is this pain?",
    "Smiling. Dancing.",
    "But not with me. Someone else.",
    "",
    "...",
    "",
    "My stomach twists into a knot. I remember. I remember who I am.",
    "But where am I?",
    "I don’t know.",
    "I don’t know.",
    "I don’t know.",
    "",
    "...",
    "",
    "The beeping gets faster.",
    "Beep. Beep. Beep. Beep. Beep.",
    "I’m angry. This feeling doesn’t sit with me. Then sadness follows.",
    "The machine slows down.",
    "",
    "...",
    "",
    "Beep. Beep. Beep.",
    "I remember. It was the party. Bright lights everywhere. The feeling of adrenaline flooded my body.",
    "Then came the drinks.",
    "One after the other, I couldn’t count which one this was.",
    "I needed to leave. Where was the door?",
    "And then",
    "",
    "...",
    "",
    "I can’t remember. A car?",
    "Where am I?",
    "What happened?",
    "",
    "...",
    "",
    "I need to know.",
    "I need to know.",
    "I need to know.",
    "I need to know.",
    "",
    "...",
    "",
    "I need to wake up.",
    "I need to wake up.",
    "",
    "...",
    "",
    "Something is pulling you forward.",
    "There are no longer doors. You did it."
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

# Main loop
running = True
while running:
    dt  = clock.tick(60)
    now = pygame.time.get_ticks()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
           event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
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

            # when story done and standing on portal:
            if story_finished and player_rect.colliderect(portal_rect):
                # first SPACE shows confirmation
                if not show_confirm:
                    if event.key == pygame.K_SPACE:
                        show_confirm = True
                else:
                    # second SPACE confirms and enters
                    pygame.quit()
                    subprocess.Popen([
                        sys.executable,
                        os.path.join(base_path, 'HospitalGame.py')
                    ])
                    sys.exit()
                continue

    # movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_rect.x -= speed
        facing_left = True
        show_confirm = False
    if keys[pygame.K_RIGHT]:
        player_rect.x += speed
        facing_left = False
        show_confirm = False
    if keys[pygame.K_UP]:
        player_rect.y -= speed
        show_confirm = False
    if keys[pygame.K_DOWN]:
        player_rect.y += speed
        show_confirm = False

    # animate player
    if now - last_anim_time >= ANIM_COOLDOWN:
        frame         = (frame + 1) % len(animation_list)
        last_anim_time = now

    # animate portal once story done
    if story_finished and now - last_portal_update >= PORTAL_COOLDOWN:
        portal_frame       = (portal_frame + 1) % len(portal_frames)
        last_portal_update = now

    # typewriter auto-advance
    if not story_finished and not line_finished:
        if (char_index < len(story_lines[current_line])
            and now - last_char_time > TYPE_DELAY):
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

    # camera follow player
    if player_rect.bottom > camera_y + SCROLL_DOWN_THRESH:
        camera_y = min(player_rect.bottom - SCROLL_DOWN_THRESH,
                       WORLD_HEIGHT - HEIGHT)
    elif player_rect.top < camera_y + SCROLL_UP_THRESH:
        camera_y = max(player_rect.top - SCROLL_UP_THRESH, 0)

    # draw world content
    world_surface.fill((0,0,0))
    for i, line in enumerate(displayed_lines):
        surf = font.render(line, True, (255,255,255))
        world_surface.blit(surf, (20, 45 + 30*i))
    if not story_finished:
        surf = font.render(current_text, True, (255,255,255))
        world_surface.blit(surf, (20, 45 + 30*len(displayed_lines)))
    if story_finished:
        world_surface.blit(portal_frames[portal_frame], portal_rect)

    # blit viewport
    screen.blit(world_surface, (0,0),
                area=pygame.Rect(0, camera_y, WIDTH, HEIGHT))

    # draw player on top
    sprite = animation_list[frame]
    if facing_left:
        sprite = pygame.transform.flip(sprite, True, False)
    screen.blit(sprite, (player_rect.x, player_rect.y - camera_y))

    # draw confirmation popup
    if show_confirm:
        bw, bh = 400, 80
        bx = portal_rect.centerx - bw//2
        by = portal_rect.top - bh - 20 - camera_y
        popup = pygame.Surface((bw, bh), pygame.SRCALPHA)
        popup.fill((0, 0, 0, 200))
        pygame.draw.rect(popup, (255,255,255), (0,0,bw,bh), 2)
        screen.blit(popup, (bx, by))
        msg1 = font.render("Are you sure you want to enter?", True, (255,255,255))
        msg2 = font2.render("Space to continue...", True, (255,255,255))
        screen.blit(msg1, (bx+20, by+20))
        screen.blit(msg2, (bx+20, by+45))

    pygame.display.flip()

pygame.quit()
sys.exit()