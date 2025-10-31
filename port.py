import pygame

class Port:
    def __init__(self, x, y, capacity, radius=10):
        self.x = x
        self.y = y
        self.capacity = capacity
        self.radius = radius
        self.docked_ships = []

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 0, 0), (self.x, self.y), self.radius)
        text = pygame.font.SysFont(None, 24).render(f'{len(self.docked_ships)}/{self.capacity}', False, (0, 0, 0))
        surface.blit(text, (self.x + self.radius + 5, self.y - self.radius))
    
    def dock_nearby_ships(self, ships):
        for ship in ships:
            if ship.docked:
                continue
            dist = ((ship.x - self.x) ** 2 + (ship.y - self.y) ** 2) ** 0.5
            if dist <= self.radius and len(self.docked_ships) < self.capacity:
                ship.dock_at_port(self)
                self.docked_ships.append(ship)
