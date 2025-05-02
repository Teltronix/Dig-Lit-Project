import pygame
import sys
import os

pygame.init()

# — Screen Setup —
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hospital Escape → Outside World")
clock = pygame.time.Clock()

# — Colors —
WHITE          = (255, 255, 255)
BLACK          = (  0,   0,   0)
BED_COLOR      = (200, 200, 255)
PLAYER_COLOR   = (255,  50,  50)
DOOR_COLOR     = (  0, 200,   0)
SIDEWALK_COLOR = (200, 200, 200)
ROAD_COLOR     = (100, 100, 100)
HOUSE_COLOR    = (150,  75,   0)
CAR_COLOR      = (  0,   0,   0)

# — Game Objects: Hospital —
bed_rect  = pygame.Rect(100, 200, 300, 120)
door_rect = pygame.Rect(WIDTH - 80, HEIGHT//2 - 60, 60, 120)

# — Player —
player_size  = 40
player_speed = 5
player = pygame.Rect(
    bed_rect.centerx - player_size//2,
    bed_rect.centery - player_size//2,
    player_size, player_size
)

# — Outside World Layout —
# Roads (horizontal + vertical cross)
road_h = pygame.Rect(0, HEIGHT//2 - 50, WIDTH, 100)
road_v = pygame.Rect(WIDTH//2 - 50, 0, 100, HEIGHT)
# Sidewalk is background color
# Houses in four quadrants around cross (excluding sidewalks)
sw = 10  # sidewalk width
houses = [
    pygame.Rect(0, 0, road_v.left - sw, road_h.top - sw),                        # top-left
    pygame.Rect(road_v.right + sw, 0, WIDTH - (road_v.right + sw), road_h.top - sw),  # top-right
    pygame.Rect(0, road_h.bottom + sw, road_v.left - sw, HEIGHT - (road_h.bottom + sw)),  # bottom-left
    pygame.Rect(road_v.right + sw, road_h.bottom + sw, WIDTH - (road_v.right + sw), HEIGHT - (road_h.bottom + sw)),  # bottom-right
]
allowed_areas = [road_h, road_v] + houses

# — Car (spawns after 10s outside) —
car = None
car_speed = 5

# — States —
IN_BED, AWAKE, OUTSIDE, HIT = range(4)
state = IN_BED
outside_start = None

# — Font —
font = pygame.font.SysFont(None, 48)

def draw_text(text, y_offset=0):
    surf = font.render(text, True, BLACK)
    rect = surf.get_rect(center=(WIDTH//2, HEIGHT//2 + y_offset))
    screen.blit(surf, rect)

running = True
while running:
    dt = clock.tick(60)
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if state == IN_BED and event.key == pygame.K_SPACE:
                state = AWAKE
            elif state == HIT and event.key == pygame.K_ESCAPE:
                running = False

    keys = pygame.key.get_pressed()

    # — State Logic —
    if state == AWAKE:
        # movement
        if keys[pygame.K_LEFT]:  player.x -= player_speed
        if keys[pygame.K_RIGHT]: player.x += player_speed
        if keys[pygame.K_UP]:    player.y -= player_speed
        if keys[pygame.K_DOWN]:  player.y += player_speed
        # bounds
        player.x = max(0, min(player.x, WIDTH  - player_size))
        player.y = max(0, min(player.y, HEIGHT - player_size))
        # door → outside
        if player.colliderect(door_rect):
            state = OUTSIDE
            # place player at door exit
            player.x = WIDTH//2
            player.y = HEIGHT//2
            outside_start = now

    elif state == OUTSIDE:
        # movement with collision against sidewalks
        old_pos = player.x, player.y
        if keys[pygame.K_LEFT]:  player.x -= player_speed
        if keys[pygame.K_RIGHT]: player.x += player_speed
        if keys[pygame.K_UP]:    player.y -= player_speed
        if keys[pygame.K_DOWN]:  player.y += player_speed
        player.x = max(0, min(player.x, WIDTH  - player_size))
        player.y = max(0, min(player.y, HEIGHT - player_size))
        # only allow if player center is in an allowed area
        if not any(area.collidepoint(player.center) for area in allowed_areas):
            player.x, player.y = old_pos

        # spawn car after 10 seconds
        if outside_start and now - outside_start >= 10000 and car is None:
            car = pygame.Rect(
                -80,
                road_h.centery - 20,
                80, 40
            )

        # move car and check hit
        if car:
            car.x += car_speed
            if car.colliderect(player):
                state = HIT

    # — Drawing —
    if state in (IN_BED, AWAKE):
        screen.fill(WHITE)
        pygame.draw.rect(screen, BED_COLOR, bed_rect)
        pygame.draw.rect(screen, DOOR_COLOR, door_rect)
        pygame.draw.rect(screen, PLAYER_COLOR, player)
        if state == IN_BED:
            draw_text("Press SPACE to wake up")
    elif state in (OUTSIDE, HIT):
        # sidewalks background
        screen.fill(SIDEWALK_COLOR)
        # draw houses
        for h in houses:
            pygame.draw.rect(screen, HOUSE_COLOR, h)
        # draw roads
        pygame.draw.rect(screen, ROAD_COLOR, road_h)
        pygame.draw.rect(screen, ROAD_COLOR, road_v)
        # draw player
        pygame.draw.rect(screen, PLAYER_COLOR, player)
        # draw car if present
        if car:
            pygame.draw.rect(screen, CAR_COLOR, car)
        if state == HIT:
            draw_text("You got hit by a car!", y_offset=-30)
            draw_text("Press ESC to quit", y_offset=40)

    pygame.display.flip()

pygame.quit()
sys.exit()