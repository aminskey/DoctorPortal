"""
*   AUTHOR:     SYED M. AMIN
*   PROJECT:    AI (ESCAPE ROOM AFLEVERING)
*   FILE:       simpleImage.py
"""

import pygame

class SimpleImage(pygame.sprite.Sprite):
    def __init__(self, image, size):
        super().__init__()

        self.image = pygame.transform.scale(pygame.image.load(image), size)
        self.rect = self.image.get_rect()
