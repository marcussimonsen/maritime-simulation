class Port:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, 10, 20)

    def draw(self, surface, debug_draw=False):
        rect = pygame.Rect(self.x, self.y, 10, 20)
        pygame.draw.rect(surface, "black", rect)

