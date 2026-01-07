import pygame
import math

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1600, 1000))
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    def draw_grid(screen, color, spacing):
        width, height = screen.get_size()
        # Draw vertical lines
        for x in range(0, width, spacing):
            pygame.draw.line(screen, color, (x, 0), (x, height), 1)
        # Draw horizontal lines
        for y in range(0, height, spacing):
            pygame.draw.line(screen, color, (0, y), (width, y), 1)

    draw_grid(screen,(70,70,70),30)

    keys = pygame.key.get_pressed()
    if True:
        player_pos.y -= 3 * dt
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt 
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()