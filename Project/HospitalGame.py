import pygame
import sys

pygame.init()

# — Screen Setup —
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Hospital Escape → Outside World")
clock = pygame.time.Clock()

# — Colors —
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BED_COLOR = (200, 200, 255)
PLAYER_COLOR = (255, 50, 50)
DOOR_COLOR = (0, 200, 0)
ROAD_TOP = (100, 100, 100)
ROAD_CENTER = (120, 120, 120)
CAR_COLOR = (0, 0, 0)
BOX_COLOR = (240, 240, 240)
BOX_BORDER = (100, 100, 100)

# — Game States —
IN_BED, AWAKE, OUTSIDE, HIT = range(4)
state = IN_BED

# — Font —
font = pygame.font.SysFont(None, 48)
def draw_text(text, y_offset=0):
    surf = font.render(text, True, BLACK)
    rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(surf, rect)

def draw_popup(text):
    popup_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 60, 400, 120)
    pygame.draw.rect(screen, BOX_COLOR, popup_rect)
    pygame.draw.rect(screen, BOX_BORDER, popup_rect, 4)
    draw_text(text)

# — Hospital Room Setup —
bed_rect  = pygame.Rect(100, 200, 300, 120)
door_rect = pygame.Rect(WIDTH - 80, HEIGHT // 2 - 60, 60, 120)
player = pygame.Rect(
    bed_rect.centerx - 20,
    bed_rect.centery - 30,
    40, 60
)

# — Outside World Scroll Setup —
scroll_x = 0
world_speed = 3
player_world_x = 0
outside_start = None

# — Car —
car = None
car_speed = world_speed + 5
car_trigger_x = 15 * world_speed * 60  # Trigger after 15 sec at 60fps

# — Main Loop —
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
            if state == IN_BED and event.key == pygame.K_SPACE:
                state = AWAKE

    keys = pygame.key.get_pressed()

    # — State Logic —
    if state == AWAKE:
        if keys[pygame.K_LEFT]:  player.x -= 5
        if keys[pygame.K_RIGHT]: player.x += 5
        if keys[pygame.K_UP]:    player.y -= 5
        if keys[pygame.K_DOWN]:  player.y += 5
        player.clamp_ip(screen.get_rect())
        if player.colliderect(door_rect):
            state = OUTSIDE
            player = pygame.Rect(WIDTH // 2 - 20, HEIGHT - 140, 40, 60)
            outside_start = now

    elif state == OUTSIDE:
        if keys[pygame.K_RIGHT]:
            scroll_x -= world_speed
            player_world_x += world_speed
        player.y = HEIGHT - 140
        if car is None and player_world_x >= car_trigger_x:
            car = pygame.Rect(-100, HEIGHT - 110, 100, 50)
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
            draw_popup("Press SPACE to wake up")

    elif state in (OUTSIDE, HIT):
        screen.fill(BLACK)
        for i in range(-2, WIDTH // 40 + 4):
            x = i * 40 + scroll_x % 40
            pygame.draw.rect(screen, ROAD_CENTER, (x, HEIGHT - 80, 40, 40))
            pygame.draw.rect(screen, ROAD_TOP, (x, HEIGHT - 40, 40, 40))
        pygame.draw.rect(screen, PLAYER_COLOR, player)
        if car:
            pygame.draw.rect(screen, CAR_COLOR, car)
        if state == HIT:
            draw_text("You got hit by a car!", y_offset=-30)
            draw_text("Press ESC to quit", y_offset=40)

    pygame.display.flip()

pygame.quit()
sys.exit()
