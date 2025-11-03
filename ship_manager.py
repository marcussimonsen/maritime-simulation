from ship import Ship
from spawn_utils import spawn_not_in_coastlines


class ShipManager:
    def __init__(self, screen_size, screen):
        self.screen_size = screen_size
        self.ships = []
        self.show_ship_sensors = True
        self.screen = screen

    def get_route_between(self, routes, departure_port, destination_port):
        return routes.get((departure_port, destination_port))

    def add_ship(self, ship: Ship):
        self.ships.append(ship)

    def spawn_random_ships(self, coastlines):
        route = None
        for _ in range(20):
            x, y = spawn_not_in_coastlines(coastlines, self.screen_size[0], self.screen_size[1], margin=50, max_attempts=2000)
            self.ships.append(Ship(x, y, route[1:-1].copy() if route else None))

    def undock_ship(self, ship, route, destination, departure):
        ship.set_route(route)
        ship.departure = departure
        ship.destination = destination
        ship.docked = False
        ship.vx = -1
        ship.vy = -1
        ship.x = route[-2][0]
        ship.y = route[-2][1]
        self.ships.append(ship)

    def send_off_ships(self, port, routes):
        for order in list(port.orders):
            route = self.get_route_between(routes, port, order.destination)
            if len(port.docked_ships) < order.containers:
                continue
            for _ in range(order.containers):
                ship = port.docked_ships.pop(0)
                self.undock_ship(ship, route, order.destination, port)
            port.orders.remove(order)

    def update_ships(self, coastlines):
        for ship in self.ships:
            ship.boundary_update(1280, 720)
            ship.flocking(self.ships)
            ship.follow_route(surface=self.screen if self.show_ship_sensors else None)
            ship.move(self.ships, coastlines, surface=self.screen if self.show_ship_sensors else None)
            ship.draw(self.screen)

    def toggle_ship_sensors(self):
        self.show_ship_sensors = not self.show_ship_sensors
