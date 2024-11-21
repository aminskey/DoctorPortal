import pygame
from pygame.locals import *

def isInBounds(x, offset, min, max):
    return (x-offset) < min or (x+offset) > max

class Text(pygame.sprite.Sprite):
    def __init__(self, msg, script, textColor, pos=(0, 0), shadow : tuple =None, pos2=(2, 3), clickable=False):
        super().__init__()

        self.msg = msg
        img = script.render(msg, None, textColor)

        self.copy = script.render(msg, None, (255, 255, 255))

        # If shadow is not None, then we must expect it to be the shadow color

        if isinstance(shadow, tuple) and len(shadow) == 3:
            self.image = pygame.Surface((img.get_width()*1.02, img.get_height()*1.02)).convert_alpha()
            self.image.fill((23, 16, 1))
            self.image.set_colorkey((23, 16, 1))

            shadowText = Text(msg, script, shadow)
            shadowText.rect.topleft = pos2

            self.image.blit(shadowText.image, shadowText.rect)
            self.image.blit(img, (0, 0))
        else:
            self.image = img.copy()
        self.base_image = self.image.copy()

        self.rect = self.image.get_rect()
        self.color = textColor
        self.rect.center = pos
        self.alphaValue = 255
        self.deltaA = -20

        self.clickable = clickable
        self.clicked = False

        self.f = None

    def blink(self):
        self.alphaValue += self.deltaA
        if not isInBounds(self.alphaValue, 1, 0, 255):
            self.deltaA *= -1
            self.alphaValue += self.deltaA
        self.image.set_alpha(self.alphaValue)

    def update(self):
        if self.clickable:
            if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                self.clicked = True
                if self.f is not None:
                    self.f()
            elif self.rect.collidepoint(pygame.mouse.get_pos()):
                self.image = self.copy
            else:
                self.image = self.base_image
                self.clicked = False


    def setClick(self, x):
        self.f = x