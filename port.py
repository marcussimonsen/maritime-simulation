import pygame

class Port:
    def __init__(self, x, y, capacity):
        self.x = x
        self.y = y
        self.capacity = capacity

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 0, 0), (self.x, self.y), 10)
