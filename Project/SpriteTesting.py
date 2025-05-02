import pygame
import spritesheet

pygame.init()

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Spritesheets')


BG = (50,50,50)
BLACK = (0, 0, 0)

# sprite insertion here
brain_sprite_image = pygame.image.load('Brain.png').convert_alpha()
sprite_sheet = spritesheet.BrainSprite(brain_sprite_image)

def get_image(sheet, frame, width,height, color):
    image = pygame.Surface((width,height)).convert_alpha()
    image.blit(sheet, (0, 0,), ((frame * width), 0, width, height))
    scale = 2
    image = pygame.transform.scale(image, (width * scale, height * scale))
    

    return image

#create animation list
animation_list = []
animation_steps = 5
last_update = pygame.time.get_ticks()
animation_cooldown = 125
frame = 0

for x in range(animation_steps):

    animation_list.append(sprite_sheet.get_image(x, 32, 32, scale = 10))




run = True
while run:
    
    screen.fill(BG)

    #upd animation
    current_time = pygame.time.get_ticks()
    if current_time - last_update >= animation_cooldown:
        frame += 1
        last_update = current_time
        if frame >= len(animation_list):
            frame = 0

    #show frame image

    screen.blit(animation_list[frame], (0, 0))

    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
