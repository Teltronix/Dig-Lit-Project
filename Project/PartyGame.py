import os
import sys
import subprocess
import pygame
import random
import string
import math
from util import resource_path

pygame.init()

def load_image(name):
    path = resource_path(name)
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
BG = pygame.image.load(resource_path('Floor.png')).convert()
clock = pygame.time.Clock()
WHITE, BLACK, GRAY = (255,255,255), (0,0,0), (80,80,80)

# — fonts —
cryptic_name = ''.join(random.choice(string.ascii_uppercase + string.digits)
                       for _ in range(6))
normal_font = pygame.font.SysFont(None, 32)
hint_font   = pygame.font.SysFont(None, 24)
gaster_font = pygame.font.Font(resource_path('wingdings.otf'), 36)
portal_font      = pygame.font.SysFont(None, 28)
portal_hint_font = pygame.font.SysFont(None, 18)

# — player setup —
player_sheet  = load_image("Person.png")
player_anim   = playerv2(player_sheet)
# note: your sheet uses 200×600 per frame
player_frames = [
    player_anim.get_image(i, 200, 600, 0.5)
    for i in range(player_sheet.get_width() // 200)
]
player_index       = 0
PLAYER_COOLDOWN    = 150
last_player_update = pygame.time.get_ticks()
facing_left        = False
player_speed       = 4
# start at true center
player = player_frames[0].get_rect(center=(SCREEN_W//2, SCREEN_H//2))

# — NPC setup —
PERSON_CLASSES = [Person1,Person2,Person3,Person4,Person5,Person6]
NPC_COOLDOWN   = 333
P_W, P_H       = 40, 56
PLAYER_SCALE   = 2.6

persons_frames = []; persons_index = []; persons_last = []; person_rects = []
cx, cy, radius = SCREEN_W//2, SCREEN_H//2, 350

for i, cls in enumerate(PERSON_CLASSES):
    sheet = load_image(f"Game2Person{i+1}.png")
    anim  = cls(sheet)
    count = sheet.get_width() // P_W
    frames = [anim.get_image(f, P_W, P_H, PLAYER_SCALE) for f in range(count)]
    persons_frames.append(frames)
    persons_index.append(random.randrange(count))
    persons_last.append(pygame.time.get_ticks() - random.randrange(NPC_COOLDOWN))
    angle = math.radians(i * 360 / len(PERSON_CLASSES))
    x = cx + math.cos(angle)*radius - (P_W*PLAYER_SCALE)/2
    y = cy + math.sin(angle)*radius - (P_H*PLAYER_SCALE)/2
    person_rects.append(pygame.Rect(int(x), int(y),
                                    P_W*PLAYER_SCALE, P_H*PLAYER_SCALE))

# — portal setup with mask collision —
portal_sheet     = load_image("portal.png")
portal_animator  = Portal(portal_sheet)
PF_W, PF_H       = 498, 498
portal_frames    = [
    portal_animator.get_image(f, PF_W, PF_H, 0.5)
    for f in range(portal_sheet.get_width() // PF_W)
]
portal_index        = 0
PORTAL_COOLDOWN     = 125
last_portal_update  = pygame.time.get_ticks()
portal_rect         = portal_frames[0].get_rect(center=(cx, cy))
portal_active       = False
portal_entered      = False

# — dialog screens unchanged —
TEXT_SCREENS = [
    "Heyyy... CRYPTIC_NAME, long time no see!",
    "You made it! Grab a drink, find a seat.",
    "You ever wonder why the lights never turn off here?",
    "Why are you here? You aren't supposed to be here.",
    "Nothing around you is real. Wake up.",
    "Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up. Wake up."
]
FINAL_MESSAGE  = "But no one was there."
next_file      = "AfterPartyGame.py"
text_index     = 0
show_text      = False
current_text   = ""
touched_indices= set()
final_played   = False
persons_cleared= False

def wrap_text(text, font, max_w):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        test = cur + w + " "
        if font.size(test)[0] < max_w:
            cur = test
        else:
            lines.append(cur.strip()); cur = w + " "
    if cur: lines.append(cur.strip())
    return lines

def draw_text_box(txt):
    BW, BH = 700, 150
    box = pygame.Rect(SCREEN_W//2 - BW//2,
                      SCREEN_H//2 - BH//2,
                      BW, BH)
    pygame.draw.rect(screen, (240,240,240), box)
    pygame.draw.rect(screen, BLACK, box, 2)
    if "CRYPTIC_NAME" in txt:
        a,b = txt.split("CRYPTIC_NAME")
        s1 = normal_font.render(a,True,BLACK)
        s2 = gaster_font.render(cryptic_name,True,BLACK)
        s3 = normal_font.render(b,True,BLACK)
        x,y = box.left+20, box.top+40
        screen.blit(s1,(x,y)); x+=s1.get_width()+10
        screen.blit(s2,(x,y)); x+=s2.get_width()+10
        screen.blit(s3,(x,y))
    else:
        lines = wrap_text(txt, normal_font, BW-40)
        for i,ln in enumerate(lines):
            surf = normal_font.render(ln,True,BLACK)
            screen.blit(surf,(box.left+20, box.top+20+i*30))
    hint = hint_font.render("Space to continue...",True,GRAY)
    screen.blit(hint,(box.centerx-hint.get_width()/2,box.bottom-30))

running = True
while running:
    now = pygame.time.get_ticks()
    dt  = clock.tick(60)

    # background centered
    bw,bh = BG.get_size()
    screen.blit(BG,((SCREEN_W-bw)//2, (SCREEN_H-bh)//2))

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running=False
        elif e.type==pygame.KEYDOWN:
            if e.key==pygame.K_ESCAPE:
                running=False
            elif show_text and e.key==pygame.K_SPACE:
                if text_index==len(TEXT_SCREENS) and not final_played:
                    current_text=FINAL_MESSAGE; final_played=True; show_text=True
                elif final_played and not persons_cleared:
                    person_rects.clear()
                    portal_active=True; show_text=False; persons_cleared=True
                else:
                    show_text=False
            # portal confirmation only when mask‐overlap
            elif portal_active and e.key==pygame.K_SPACE:
                # re‐compute masks & offset
                pf = player_frames[player_index]
                pm = pygame.mask.from_surface(pf)
                portal_surf = portal_frames[portal_index]
                qm = pygame.mask.from_surface(portal_surf)
                off = (portal_rect.x - player.x, portal_rect.y - player.y)
                if pm.overlap(qm, off):
                    portal_entered=True; running=False

    # movement & npc dialog
    keys = pygame.key.get_pressed()
    moving=False
    if not show_text:
        if keys[pygame.K_LEFT]:
            player.x-=player_speed; facing_left=True; moving=True
        if keys[pygame.K_RIGHT]:
            player.x+=player_speed; facing_left=False;moving=True
        if keys[pygame.K_UP]:
            player.y-=player_speed; moving=True
        if keys[pygame.K_DOWN]:
            player.y+=player_speed; moving=True
        player.clamp_ip(screen.get_rect())
        # npc mask collisions
        pf = player_frames[player_index]
        pm = pygame.mask.from_surface(pf)
        for i,rect in enumerate(person_rects):
            nf = persons_frames[i][persons_index[i]]
            nm = pygame.mask.from_surface(nf)
            off=(rect.x-player.x,rect.y-player.y)
            if pm.overlap(nm, off) and i not in touched_indices:
                current_text=TEXT_SCREENS[text_index]
                touched_indices.add(i)
                text_index+=1
                show_text=True
                break

    # animate player
    if moving and now-last_player_update>PLAYER_COOLDOWN:
        player_index=(player_index+1)%len(player_frames)
        last_player_update=now
    elif not moving:
        player_index=0

    # animate NPCs
    for i in range(len(persons_frames)):
        if now-persons_last[i]>NPC_COOLDOWN:
            persons_index[i]=(persons_index[i]+1)%len(persons_frames[i])
            persons_last[i]=now

    # animate portal
    if portal_active and now-last_portal_update>PORTAL_COOLDOWN:
        portal_index=(portal_index+1)%len(portal_frames)
        last_portal_update=now

    # draw portal first
    if portal_active:
        screen.blit(portal_frames[portal_index], (portal_rect.x, portal_rect.y))
        # portal prompt
        pf=player_frames[player_index]; pm=pygame.mask.from_surface(pf)
        qm=pygame.mask.from_surface(portal_frames[portal_index])
        off=(portal_rect.x-player.x, portal_rect.y-player.y)
        if pm.overlap(qm, off):
            BW,BH=180,60
            bx,by=portal_rect.centerx-BW//2, portal_rect.top-BH-10
            pygame.draw.rect(screen,(240,240,240),(bx,by,BW,BH))
            pygame.draw.rect(screen,BLACK,(bx,by,BW,BH),2)
            l1=portal_font.render("Enter?",True,BLACK)
            l2=portal_hint_font.render("Space to continue",True,GRAY)
            screen.blit(l1,(bx+10,by+8))
            screen.blit(l2,(bx+10,by+8+l1.get_height()+2))

    # draw player on top of portal
    pf = player_frames[player_index]
    if facing_left:
        pf = pygame.transform.flip(pf,True,False)
    screen.blit(pf,(player.x,player.y))

    # draw NPCs
    for i,rect in enumerate(person_rects):
        f=persons_frames[i][persons_index[i]]
        if rect.centerx<SCREEN_W//2:
            f=pygame.transform.flip(f,True,False)
        screen.blit(f,(rect.x,rect.y))

    # dialog box
    if show_text:
        draw_text_box(current_text)

    pygame.display.flip()

pygame.quit()

if portal_entered:
    subprocess.Popen([sys.executable, resource_path(next_file)])
    sys.exit()