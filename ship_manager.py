from ship import Ship
from spawn_utils import spawn_not_in_coastlines
from route import Route


class ShipManager:
    def __init__(self, screen_size, screen, routes):
        self.screen_size = screen_size
        self.ships = []
        self.show_ship_sensors = True
        self.screen = screen
        self.send_ships_immidiately = True

    def get_route_between(self, routes, departure_port, destination_port):
        return routes.get((departure_port, destination_port))

    def add_ship(self, ship: Ship):
        self.ships.append(ship)

    def remove_ship(self, ship: Ship):
        # WARN: Linear running time in the amount of ships
        if ship in self.ships:
            self.ships.remove(ship)

    def spawn_random_ships(self, coastlines):
        route = None
        for _ in range(20):
            x, y = spawn_not_in_coastlines(coastlines, self.screen_size[0], self.screen_size[1], margin=50, max_attempts=2000)
            self.ships.append(Ship(x, y, route[1:-1].copy() if route else None))

    def undock_ship(self, ship, route, destination, departure):
        ship.undock(Route(route, departure, destination))
        self.add_ship(ship)

    def dock_ship(self, port, ship):
        ship.dock(port)
        self.remove_ship(ship)
        port.add_docked_ship(ship)

    def send_off_ships(self, routes, port):
        for order in list(port.orders):
            route = self.get_route_between(routes, port, order.destination)
            if len(port.docked_ships) < order.containers:
                continue
            for _ in range(order.containers):
                ship = port.docked_ships.pop(0)
                self.undock_ship(ship, route, order.destination, port)
            port.remove_order(order)

    def update_ships(self, coastlines):
        for ship in self.ships:
            ship.boundary_update(1280, 720)
            ship.flocking(self.ships, surface=self.screen if self.show_ship_sensors else None)
            ship.follow_route(surface=self.screen if self.show_ship_sensors else None)
            ship.move(self.ships, coastlines, surface=self.screen if self.show_ship_sensors else None)
            ship.draw(self.screen)

    def update_ports(self, ports, routes):
        for port in ports:
            self.dock_nearby_ships_to_destination_dock(port)
            if self.send_ships_immidiately:
                # TODO: fix this
                self.send_off_ships(routes, port)
            port.draw(self.screen)

    def dock_nearby_ships_to_destination_dock(self, port):
        padding = 15
        for ship in self.ships:
            if ship.destination is None:  # Ignore ships that do not have a route - this is irrelevant for us, we don't want this
                continue
            dist = ((ship.x - port.x) ** 2 + (ship.y - port.y) ** 2) ** 0.5
            if dist <= port.radius + padding and len(port.docked_ships) < port.capacity and ship.destination is port:
                self.dock_ship(port, ship)

    def toggle_send_ships_immidiately(self):
        self.send_ships_immidiately = not self.send_ships_immidiately

    def toggle_ship_sensors(self):
        self.show_ship_sensors = not self.show_ship_sensors
