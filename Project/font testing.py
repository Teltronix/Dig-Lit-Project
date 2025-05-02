import pygame
pygame.init()

screen = pygame.display.set_mode((400, 200))
font = pygame.font.Font("wingdings.otf", 64)
text = font.render("HELLO", True, (0, 0, 0))
screen.fill((255, 255, 255))
screen.blit(text, (50, 70))
pygame.display.flip()
pygame.time.wait(2000)
pygame.quit()
