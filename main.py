import pygame


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True
    dt = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))

        # Render stuff here

        pygame.display.flip()
        dt = clock.tick(60) / 1000 # limits FPS and
    pygame.quit()

if __name__ == "__main__":
    main()
