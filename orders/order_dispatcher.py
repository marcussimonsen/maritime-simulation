import random

def add_random_orders(ports):
    max_containers_per_order = 4

    for port in ports:
        if add_ports_randomly is False:
            break
        dest_port = random.choice(ports)
        while dest_port == port:
            dest_port = random.choice(ports)

        number_of_containers = random.randint(1, max_containers_per_order)
        port.add_order(Order(dest_port, number_of_containers))
        for _ in range(number_of_containers):
            ship = Ship(port.x, port.y)
