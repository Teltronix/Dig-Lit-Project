import pygame

pygame.init()

# Screen setup
screen = pygame.display.set_mode((480, 480))
pygame.display.set_caption("Maybe go left (you lost)")

# Load and scale background image
background = pygame.image.load("winbg.png").convert()
background = pygame.transform.scale(background, (480, 480))  # ✅ FIXED

# Font setup
font = pygame.font.SysFont(None, 72)
red = (255, 0, 0)
text = font.render("YOU WIN!!!", True, red)
text_rect = text.get_rect(center=(240, 240))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(background, (0, 0))      # ✅ Draw background
    screen.blit(text, text_rect)         # ✅ Draw centered text
    pygame.display.update()              # ✅ Show everything

pygame.quit()
