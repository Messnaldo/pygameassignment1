import pygame
from constant import *

class Paddle:
    def __init__(self, screen, x, y, width, height, color):
        self.screen = screen

        self.rect = pygame.Rect(x, y, width, height)
        self.dy = 0
        self.default_color = color
        self.color = color
        self.default_height = height

    def update(self, dt):
        if self.dy > 0:
            if self.rect.y + self.rect.height < HEIGHT:
                self.rect.y += self.dy*dt
        else:
            if self.rect.y >= 0:
                self.rect.y += self.dy*dt

    def render(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
    def reset_color(self):
        self.color = self.default_color
    def reset_size(self):
        self.rect.height = self.default_height
