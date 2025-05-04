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

def load_image(name, alpha=True):
    path = os.path.join(BASE_PATH, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing asset: {path}")
    img = pygame.image.load(path)
    return img.convert_alpha() if alpha else img.convert()

# — sprite‐sheet helper —
class SpriteSheet:
    def __init__(self, sheet): self.sheet = sheet
    def get_image(self, frame, w, h, scale=1):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.blit(self.sheet, (0,0), (frame*w, 0, w, h))
        if scale != 1:
            surf = pygame.transform.scale(surf, (int(w*scale), int(h*scale)))
        return surf

# — fullscreen & sizing —
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
W, H = screen.get_size()
clock = pygame.time.Clock()

# — colors & fonts —
WHITE, BLACK, GRAY = (255,255,255), (0,0,0), (80,80,80)
f32 = pygame.font.SysFont(None, 32)
f28 = pygame.font.SysFont(None, 28)

# — load & scale backgrounds —
bg_hosp  = load_image("Hospitalroom.png", alpha=False)
bg_hosp  = pygame.transform.scale(bg_hosp, (W, H))
bg_grass = load_image("GrassArea.png",  alpha=False)
bg_grass = pygame.transform.scale(bg_grass, (W, H))

# — bed & IV, 6× / 7× scale —
bed = load_image("Bed.png"); bw, bh = bed.get_size()
bed = pygame.transform.scale(bed, (bw*6, bh*6))
iv  = load_image("IV.png"); iw, ih = iv.get_size()
iv  = pygame.transform.scale(iv, (iw*7, ih*7))

# — door image, 6× scale, on right side with 50px margin —
door_img = load_image("Palm_Wood_Door.png")
dw, dh = door_img.get_size()
door_img = pygame.transform.scale(door_img, (dw*6, dh*6))
door_rect = door_img.get_rect(midright=(W-50, H//2))

# — player sprite (NPC.png: 40×56) with 2.6× scale —
player_sheet = load_image("NPC.png")
pss = SpriteSheet(player_sheet)
P_W, P_H = 40, 56
NUM_FRAMES = player_sheet.get_width() // P_W

walk_frames  = [
    pss.get_image(i, P_W, P_H, 2.6)
    for i in range(NUM_FRAMES)
]
sleep_frame  = pss.get_image(0, P_W, P_H, 2.6)  # sleeping frame, also 2.6×
player_idx       = 0
PLAYER_CD        = 150
last_player_time = pygame.time.get_ticks()
facing_left      = True   # True = facing right, False = facing left
player_speed     = 4

# bed position for midbottom
bed_midbot = (W//4, int(H*2/3))
# start sleeping on bed
player = sleep_frame.get_rect(midbottom=bed_midbot)

# — cherry blossom for grass slide (15×) —
cb_sheet = load_image("Cherry_Blossom.png")
cb_ss    = SpriteSheet(cb_sheet)
CB_H     = cb_sheet.get_height()
CB_FRAMES= cb_sheet.get_width() // CB_H
cherry_frames = [
    cb_ss.get_image(i, CB_H, CB_H, 15)
    for i in range(CB_FRAMES)
]
ch_idx      = 0
CHERRY_CD   = 200
last_cherry = pygame.time.get_ticks()

# — credits text & scroll pos —
credits = [
    "Congratulations",
    "Digital Literary Project",
    "Matthew Nowak and Andrew Bae",
    "Thank you for Playing",
    "",
    "(Press ESC to exit)"
]
cred_y = H

# — state machine —
state = "wake"   # wake → hospital → grass → credits
running = True
while running:
    now = pygame.time.get_ticks()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if state == "wake" and e.key == pygame.K_SPACE:
                # wake up: stay on bed but switch to hospital logic
                state = "hospital"
                player = walk_frames[0].get_rect(midbottom=bed_midbot)
                facing_left = True
            elif state == "grass" and e.key == pygame.K_SPACE:
                state = "credits"
            elif state == "credits" and e.key == pygame.K_ESCAPE:
                running = False

    screen.fill(WHITE)

    if state == "wake":
        screen.blit(bg_hosp, (0,0))
        # bed & IV
        bed_r = bed.get_rect(midbottom=bed_midbot)
        iv_r  = iv.get_rect(midleft=(bed_r.right + 20, bed_r.centery))
        screen.blit(bed, bed_r)
        screen.blit(iv, iv_r)
        # sleeping player rotated CCW 90°
        sf = pygame.transform.rotate(sleep_frame, 90)
        screen.blit(sf, sf.get_rect(midbottom=bed_midbot))
        # prompt
        txt = f32.render("Press SPACE to wake up", True, BLACK)
        screen.blit(txt, txt.get_rect(center=(W//2, 50)))

    elif state == "hospital":
        screen.blit(bg_hosp, (0,0))
        # bed & IV on left
        bed_r = bed.get_rect(midbottom=bed_midbot)
        iv_r  = iv.get_rect(midleft=(bed_r.right + 20, bed_r.centery))
        screen.blit(bed, bed_r)
        screen.blit(iv, iv_r)
        # door on right
        screen.blit(door_img, door_rect)
        # movement & animation
        keys = pygame.key.get_pressed()
        moving = False
        if keys[pygame.K_LEFT]:
            player.x -= player_speed
            facing_left = False   # left arrow → face left
            moving = True
        if keys[pygame.K_RIGHT]:
            player.x += player_speed
            facing_left = True    # right arrow → face right
            moving = True
        if keys[pygame.K_UP]:
            player.y -= player_speed
            moving = True
        if keys[pygame.K_DOWN]:
            player.y += player_speed
            moving = True
        player.clamp_ip(screen.get_rect())
        if moving and now - last_player_time > PLAYER_CD:
            player_idx = (player_idx + 1) % len(walk_frames)
            last_player_time = now
        elif not moving:
            player_idx = 0
        img = walk_frames[player_idx]
        if facing_left:
            img = pygame.transform.flip(img, True, False)
        screen.blit(img, player)
        # door → grass
        if player.colliderect(door_rect):
            state = "grass"

    elif state == "grass":
        screen.blit(bg_grass, (0,0))
        # cherry animation
        if now - last_cherry > CHERRY_CD:
            ch_idx = (ch_idx + 1) % len(cherry_frames)
            last_cherry = now
        tree = cherry_frames[ch_idx]
        screen.blit(tree, tree.get_rect(center=(W//2, H//2)))
        # player in grass room (idle)
        pg = walk_frames[0]
        if facing_left:
            pg = pygame.transform.flip(pg, True, False)
        screen.blit(pg, pg.get_rect(midbottom=(W//2, H-50)))
        # prompt
        txt = f28.render("Press SPACE to continue", True, BLACK)
        screen.blit(txt, txt.get_rect(center=(W//2, H-100)))

    elif state == "credits":
        screen.fill(WHITE)
        cred_y -= 1
        for i, line in enumerate(credits):
            surf = f32.render(line, True, BLACK)
            screen.blit(surf, (W//2 - surf.get_width()//2, cred_y + i*50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()