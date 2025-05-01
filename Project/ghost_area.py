
import pygame
import sys
import spritesheet

pygame.init()

# Screen setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Ghost World")
clock = pygame.time.Clock()

# Load ghost sprite sheet
ghost_sprite_image = pygame.image.load('Ghost.png').convert_alpha()
ghost_sheet = spritesheet.Ghost(ghost_sprite_image)
ghost_frames = [ghost_sheet.get_image(i, 32, 32, scale=9) for i in range(4)]
ghost_frame = 0
ghost_cooldown = 125
ghost_last_update = pygame.time.get_ticks()

# Ghost position
ghost_rect = ghost_frames[0].get_rect(center=(WIDTH // 2, HEIGHT // 2))
ghost_speed = 4

# Font and text
font = pygame.font.SysFont(None, 32)
floating_text = [
    "The silence is loud here.",
    "Is this... the end?",
    "Or the beginning of something else?",
    "Move with arrow keys.",
    "Press ESC to quit."
]

running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        ghost_rect.x -= ghost_speed
    if keys[pygame.K_RIGHT]:
        ghost_rect.x += ghost_speed
    if keys[pygame.K_UP]:
        ghost_rect.y -= ghost_speed
    if keys[pygame.K_DOWN]:
        ghost_rect.y += ghost_speed
    if keys[pygame.K_ESCAPE]:
        running = False

    # Animate ghost
    now = pygame.time.get_ticks()
    if now - ghost_last_update >= ghost_cooldown:
        ghost_last_update = now
        ghost_frame = (ghost_frame + 1) % len(ghost_frames)

    # Drawing
    screen.fill((0, 0, 0))
    screen.blit(ghost_frames[ghost_frame], ghost_rect)

    for i, line in enumerate(floating_text):
        text_surface = font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (30, 30 + i * 30))

    pygame.display.flip()

pygame.quit()
sys.exit()
