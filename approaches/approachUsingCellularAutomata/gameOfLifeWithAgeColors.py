import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Grid size
width, height = 800, 800
size = (width, height)

# Initialize the screen
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Cellular Automaton with Age Colors")

# Cell dimensions
cell_size = 10
num_cells_w = width // cell_size
num_cells_h = height // cell_size

# Grid - random initialization
grid = np.random.randint(0, 2, (num_cells_w, num_cells_h), dtype=int)

def color_by_age(age):
    if age > 0:
        # Adjust the color based on age
        return min(age * 5, 255), min(age * 10, 255), 255
    return 0, 0, 0

def draw_grid():
    for x in range(0, width, cell_size):
        for y in range(0, height, cell_size):
            age = grid[x // cell_size][y // cell_size]
            color = color_by_age(age)
            rect = pygame.Rect(x, y, cell_size, cell_size)
            pygame.draw.rect(screen, color, rect)

def update_grid():
    global grid
    new_grid = np.zeros((num_cells_w, num_cells_h), dtype=int)
    for x in range(num_cells_w):
        for y in range(num_cells_h):
            # Count living neighbors
            neighbors = np.sum(grid[max(x-1,0):min(x+2,num_cells_w), max(y-1,0):min(y+2,num_cells_h)])
            if grid[x, y] > 0:
                neighbors -= 1

            # Apply rules of the Game of Life
            if grid[x, y] > 0:
                if 2 <= neighbors <= 3:
                    # Cell stays alive
                    new_grid[x, y] = grid[x, y] + 1
            elif neighbors == 3:
                # Cell is born
                new_grid[x, y] = 1
    grid = new_grid

# Main loop
running = True
while running:
    screen.fill((0, 0, 0))
    draw_grid()
    pygame.display.flip()

    update_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
