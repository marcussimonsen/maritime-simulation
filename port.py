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
        surface.blit(text, (self.x + self.radius + 5, self.y - self.radius))


    def dock_nearby_ships(self, ships):
        for ship in ships:
            if ship.docked:
                continue
            if ship.destination != None and ship.destination != self:
                continue
            dist = ((ship.x - self.x) ** 2 + (ship.y - self.y) ** 2) ** 0.5
            if dist <= self.radius and len(self.docked_ships) < self.capacity:
                ship.dock_at_port(self)

    def send_off_ships(self):
        for order in list(self.orders):
            if len(self.docked_ships) < order.containers:
                continue
            for _ in range(order.containers):
                ship = self.docked_ships.pop(0)
                ship.undock(order.destination)
            self.orders.remove(order)

    def add_order(self, order):
        self.orders.append(order)
