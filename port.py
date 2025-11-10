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

    def add_order(self, order):
        self.orders.append(order)

    def remove_order(self, order):
        # WARN: Linear running time in the amount of orders
        self.orders.remove(order)

    def add_docked_ship(self, ship):
        self.docked_ships.append(ship)

    def remove_docked_ship(self, ship):
        # WARN: Linear running time in the amount of orders
        self.docked_ships.remove(ship)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        text = pygame.font.SysFont(None, 24).render(f'{len(self.docked_ships)}/{self.capacity}', False, (0, 0, 0))
        surface.blit(text, (self.x + 15, self.y - self.radius))
