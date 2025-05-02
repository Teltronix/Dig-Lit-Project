import pygame

class BrainSprite():
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        if scale != 1:
            image = pygame.transform.scale(image, (width * scale, height * scale))
        return image

class Car():
    def __init__(self, image):
        self.sheet = image
    
    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        if scale != 1:
            image = pygame.transform.scale(image, (width * scale, height * scale))
        return image
    
class Ghost():
    def __init__(self, image):
        self.sheet = image
    
    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        if scale != 1:
            image = pygame.transform.scale(image, (width * scale, height * scale))
        return image

class playerv1():
    def __init__(self, image):
        self.sheet = image
    
    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        if scale != 1:
            image = pygame.transform.scale(image, (width * scale, height * scale))
        return image

class playerv2():
    def __init__(self, image):
        self.sheet = image
    
    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        if scale != 1:
            image = pygame.transform.scale(image, (width * scale, height * scale))
        return image
    
class Person1():
    def __init__(self, image):
        self.sheet = image
    
    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        if scale != 1:
            image = pygame.transform.scale(image, (width * scale, height * scale))
        return image
    
class Person2():
    def __init__(self, image):
        self.sheet = image
    
    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        if scale != 1:
            image = pygame.transform.scale(image, (width * scale, height * scale))
        return image
    
class Person3():
    def __init__(self, image):
        self.sheet = image
    
    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        if scale != 1:
            image = pygame.transform.scale(image, (width * scale, height * scale))
        return image
    
class Person4():
    def __init__(self, image):
        self.sheet = image
    
    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        if scale != 1:
            image = pygame.transform.scale(image, (width * scale, height * scale))
        return image
    
class Person5():
    def __init__(self, image):
        self.sheet = image
    
    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        if scale != 1:
            image = pygame.transform.scale(image, (width * scale, height * scale))
        return image
    
class Person6():
    def __init__(self, image):
        self.sheet = image
    
    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        if scale != 1:
            image = pygame.transform.scale(image, (width * scale, height * scale))
        return image