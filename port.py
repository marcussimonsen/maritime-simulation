import pygame


class Port:
    def __init__(self, x, y, capacity, radius=10):
        self.x = x
        self.y = y
        self.capacity = capacity
        self.radius = radius
        self.docked_ships = []
        self.orders = []
        self.color = (255, 0, 0)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        text = pygame.font.SysFont(None, 24).render(f'{len(self.docked_ships)}/{self.capacity}', False, (0, 0, 0))
        surface.blit(text, (self.x + 15, self.y - self.radius))

    def dock_nearby_ships(self, ship_manager):
        padding = 15
        for ship in ship_manager.ships:
            if ship.departure is not None and ship.departure == self:
                continue
            dist = ((ship.x - self.x) ** 2 + (ship.y - self.y) ** 2) ** 0.5
            if dist <= self.radius + padding and len(self.docked_ships) < self.capacity:
                ship_manager.dock_ship(self, ship)

    def add_order(self, order):
        self.orders.append(order)
