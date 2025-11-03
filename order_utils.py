import random
from order import Order
from ship import Ship


def add_random_orders(ports, max_containers_per_order=4):
    for port in ports:
        dest_port = random.choice(ports)
        while dest_port == port:
            dest_port = random.choice(ports)

        number_of_containers = random.randint(1, max_containers_per_order)
        port.add_order(Order(dest_port, number_of_containers))
        for _ in range(number_of_containers):
            ship = Ship(port.x, port.y)
            ship.dock_at_port(port)
