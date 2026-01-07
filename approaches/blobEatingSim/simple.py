import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Define screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blob Simulation")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Define Blob class
class Blob:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 10
        self.speed = 2

    def move_towards(self, target_x, target_y):
        angle = math.atan2(target_y - self.y, target_x - self.x)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)

        # Shrink blob slightly each time it moves
        self.size -= 0.01
        if self.size < 1:
            self.size = 1

    def grow(self, amount):
        self.size += amount

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), int(self.size))

# Define Food class
class Food:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = 5

    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (self.x, self.y), self.size)

# Function to spawn food randomly
def spawn_food():
    return Food()

# Main simulation loop
def main():
    clock = pygame.time.Clock()
    blobs = [Blob(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(5)]
    foods = [spawn_food() for _ in range(10)]
    running = True

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update blob positions and check for food consumption
        for blob in blobs:
            if foods:
                closest_food = min(foods, key=lambda food: math.hypot(blob.x - food.x, blob.y - food.y))
                blob.move_towards(closest_food.x, closest_food.y)

                # Check if blob has reached the food
                if math.hypot(blob.x - closest_food.x, blob.y - closest_food.y) < blob.size:
                    blob.grow(2)  # Grow the blob
                    foods.remove(closest_food)  # Remove the consumed food
                    foods.append(spawn_food())  # Spawn a new food

            blob.draw(screen)

        # Draw all the food
        for food in foods:
            food.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
