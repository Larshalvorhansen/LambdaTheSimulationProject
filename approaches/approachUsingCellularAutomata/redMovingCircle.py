import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Random Moving Circle')

# Circle properties
circle_radius = 20
circle_color = (255, 0, 0)  # Red color
circle_x = width // 2
circle_y = height // 2

def random_movement():
    return random.choice([-1, 1])

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Random movement
    circle_x += random_movement()
    circle_y += random_movement()

    # Boundary checking
    if circle_x < circle_radius or circle_x > width - circle_radius:
        circle_x = max(circle_radius, min(circle_x, width - circle_radius))
    if circle_y < circle_radius or circle_y > height - circle_radius:
        circle_y = max(circle_radius, min(circle_y, height - circle_radius))

    # Redraw
    screen.fill((0, 0, 0))  # Clear the screen
    pygame.draw.circle(screen, circle_color, (circle_x, circle_y), circle_radius)
    pygame.display.flip()
    pygame.time.delay(10)

pygame.quit()
