import os
import sys
import subprocess
import pygame
import random
import string
import math

pygame.init()

# — paths & helper —
try:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_PATH = os.getcwd()

def load_image(name):
    path = os.path.join(BASE_PATH, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing asset: {path}")
    return pygame.image.load(path).convert_alpha()

# — sprite‐sheet animator classes —
class playerv2:
    def __init__(self, sheet): self.sheet = sheet
    def get_image(self, frame, w, h, scale):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.blit(self.sheet, (0, 0), (frame * w, 0, w, h))
        if scale != 1:
            surf = pygame.transform.scale(surf, (int(w*scale), int(h*scale)))
        return surf

class Person1(playerv2): pass
class Person2(playerv2): pass
class Person3(playerv2): pass
class Person4(playerv2): pass
class Person5(playerv2): pass
class Person6(playerv2): pass

class Portal(playerv2): pass

# — full‐screen & background color —
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_W, SCREEN_H = screen.get_size()
pygame.display.set_caption("Party Game")
BG = pygame.image.load("Floor.png").convert()
clock = pygame.time.Clock()
WHITE = (255, 255, 255)

# — cryptic name & fonts —
cryptic_name = ''.join(random.choice(string.ascii_uppercase + string.digits)
                       for _ in range(6))
normal_font = pygame.font.SysFont(None, 32)
hint_font   = pygame.font.SysFont(None, 24)
gaster_font = pygame.font.Font(os.path.join(BASE_PATH, "wingdings.otf"), 36)

# — player setup using playerv2 on NPC.png (40×56 frames) —
player_sheet  = load_image("NPC.png")
player_anim   = playerv2(player_sheet)
P_W, P_H      = 40, 56
PLAYER_SCALE  = 2
player_frames = [
    player_anim.get_image(i, P_W, P_H, PLAYER_SCALE)
    for i in range(player_sheet.get_width() // P_W)
]
player_index       = 0
PLAYER_COOLDOWN    = 150
last_player_update = pygame.time.get_ticks()
facing_left        = False

# start player down by 150 px
player = player_frames[0].get_rect(
    center=(SCREEN_W//2, SCREEN_H//2 + 150)
)
player_speed = 4

# — NPC setup (6 persons, 40×56 frames @3fps) in a circle, random start frame —
PERSON_CLASSES = [Person1, Person2, Person3, Person4, Person5, Person6]
NPC_COOLDOWN   = 333

persons_frames = []
persons_index  = []
persons_last   = []
person_rects   = []

# circle parameters, moved down by 150 px
cx, cy = SCREEN_W//2, SCREEN_H//2
radius = 300

for i, cls in enumerate(PERSON_CLASSES):
    sheet = load_image(f"Game2Person{i+1}.png")
    anim  = cls(sheet)
    count = sheet.get_width() // P_W
    frames = [anim.get_image(f, P_W, P_H, PLAYER_SCALE) for f in range(count)]
    persons_frames.append(frames)
    # randomize starting frame and timing
    persons_index.append(random.randrange(count))
    persons_last.append(pygame.time.get_ticks() - random.randrange(NPC_COOLDOWN))

    angle = math.radians(i * 360 / len(PERSON_CLASSES))
    x = cx + math.cos(angle)*radius - (P_W*PLAYER_SCALE)/2
    y = cy + math.sin(angle)*radius - (P_H*PLAYER_SCALE)/2
    rect = pygame.Rect(int(x), int(y), P_W*PLAYER_SCALE, P_H*PLAYER_SCALE)
    person_rects.append(rect)

# — portal setup (498×498 @ 0.5), centered and moved down by 150 px —
portal_sheet      = load_image("portal.png")
portal_animator   = Portal(portal_sheet)
PF_W, PF_H        = 498, 498
portal_frames     = [
    portal_animator.get_image(f, PF_W, PF_H, 0.5)
    for f in range(portal_sheet.get_width() // PF_W)
]
portal_index        = 0
PORTAL_COOLDOWN     = 125
last_portal_update  = pygame.time.get_ticks()
portal_rect = portal_frames[0].get_rect(center=(cx, cy))
portal_active       = False
portal_entered      = False

# — dialog text screens (unchanged) —
TEXT_SCREENS = [
    "Heyyy... CRYPTIC_NAME, long time no see!",
    "You made it! Grab a drink, find a seat.",
    "You ever wonder why the lights never turn off here?",
    "Why are you here? You aren't suppose to be here.",
    "Nothing around you is real. Wake up.",
    "Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. "
]
FINAL_MESSAGE  = "But no one was there."
next_file      = "AfterPartyGame.py"

text_index      = 0
show_text       = False
current_text    = ""
touched_indices = set()
final_played    = False
persons_cleared = False

def wrap_text(text, font, max_w):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        test = cur + w + " "
        if font.size(test)[0] < max_w:
            cur = test
        else:
            lines.append(cur.strip())
            cur = w + " "
    if cur:
        lines.append(cur.strip())
    return lines

def draw_text_box(txt):
    BW, BH = 700, 150
    box = pygame.Rect(SCREEN_W//2 - BW//2,
                      SCREEN_H//2 - BH//2,
                      BW, BH)
    pygame.draw.rect(screen, (240,240,240), box)
    pygame.draw.rect(screen, (50,50,50), box, 4)

    if "CRYPTIC_NAME" in txt:
        a, b = txt.split("CRYPTIC_NAME")
        s1 = normal_font.render(a, True, (0,0,0))
        s2 = gaster_font.render(cryptic_name, True, (0,0,0))
        s3 = normal_font.render(b, True, (0,0,0))
        x, y = box.left+20, box.top+40
        screen.blit(s1, (x,y)); x += s1.get_width()+10
        screen.blit(s2, (x,y)); x += s2.get_width()+10
        screen.blit(s3, (x,y))
    else:
        lines = wrap_text(txt, normal_font, BW - 40)
        for i, ln in enumerate(lines):
            surf = normal_font.render(ln, True, (0,0,0))
            screen.blit(surf, (box.left+20, box.top+20 + i*30))

    hint = hint_font.render("Space to continue...", True, (80,80,80))
    screen.blit(hint,
                (box.centerx - hint.get_width()/2,
                 box.bottom-30))

# — main loop —
running = True
while running:
    now = pygame.time.get_ticks()
    dt  = clock.tick(60)

    # compute top‐left so BG is centered
    bg_w, bg_h = BG.get_size()
    x = (SCREEN_W - bg_w) // 2
    y = (SCREEN_H - bg_h) // 2
    screen.blit(BG, (x, y))

    # events
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                running = False
            elif show_text and e.key == pygame.K_SPACE:
                if text_index == len(TEXT_SCREENS) and not final_played:
                    current_text = FINAL_MESSAGE
                    final_played = True
                    show_text    = True
                elif final_played and not persons_cleared:
                    person_rects.clear()
                    portal_active   = True
                    show_text       = False
                    persons_cleared = True
                else:
                    show_text = False

    # movement & dialog
    keys   = pygame.key.get_pressed()
    moving = False
    if not show_text:
        if keys[pygame.K_LEFT]:
            player.x -= player_speed
            facing_left = False
            moving = True
        if keys[pygame.K_RIGHT]:
            player.x += player_speed
            facing_left = True
            moving = True
        if keys[pygame.K_UP]:
            player.y -= player_speed
            moving = True
        if keys[pygame.K_DOWN]:
            player.y += player_speed
            moving = True

        player.clamp_ip(screen.get_rect())

        for i, rect in enumerate(person_rects):
            if player.colliderect(rect) and i not in touched_indices:
                if text_index < len(TEXT_SCREENS):
                    current_text = TEXT_SCREENS[text_index]
                    touched_indices.add(i)
                    text_index += 1
                    show_text   = True
                break

        if portal_active and player.colliderect(portal_rect):
            portal_entered = True
            running = False

    # animate player
    if moving and now - last_player_update > PLAYER_COOLDOWN:
        player_index = (player_index + 1) % len(player_frames)
        last_player_update = now
    elif not moving:
        player_index = 0

    # animate NPCs
    for i in range(len(persons_frames)):
        if now - persons_last[i] > NPC_COOLDOWN:
            persons_index[i] = (persons_index[i] + 1) % len(persons_frames[i])
            persons_last[i]  = now

    # animate portal
    if portal_active and now - last_portal_update > PORTAL_COOLDOWN:
        portal_index       = (portal_index + 1) % len(portal_frames)
        last_portal_update = now

    for i, rect in enumerate(person_rects):
        frame = persons_frames[i][persons_index[i]]
        # flip left‐side NPCs so they face right
        if rect.centerx < SCREEN_W//2:
            frame = pygame.transform.flip(frame, True, False)
        screen.blit(frame, (rect.x, rect.y))

    pf = player_frames[player_index]
    if facing_left:
        pf = pygame.transform.flip(pf, True, False)
    screen.blit(pf, (player.x, player.y))

    if portal_active:
        screen.blit(portal_frames[portal_index],
                    (portal_rect.x, portal_rect.y))

    if show_text:
        draw_text_box(current_text)

    pygame.display.flip()

pygame.quit()

if portal_entered:
    subprocess.Popen([sys.executable,
                      os.path.join(BASE_PATH, next_file)])
    sys.exit()