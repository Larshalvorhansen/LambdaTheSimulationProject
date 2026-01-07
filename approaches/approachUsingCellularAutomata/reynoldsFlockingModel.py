import pygame
import random
import pygame_gui
import math

# Initialize Pygame and Pygame GUI
pygame.init()
pygame.display.set_caption('Boids Simulation with Sliders')
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Pygame GUI manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Boid parameters (set initial values)
NUM_BOIDS = 100
MAX_SPEED = 4
MAX_FORCE = 0.1
SEPARATION_RADIUS = 25
ALIGNMENT_RADIUS = 50
COHESION_RADIUS = 50

# Create sliders and labels for real-time control
separation_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((10, 30), (200, 30)), start_value=SEPARATION_RADIUS, value_range=(10, 100), manager=manager)
separation_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((10, 10), (200, 20)), text='Separation Radius', manager=manager)

alignment_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((10, 80), (200, 30)), start_value=ALIGNMENT_RADIUS, value_range=(10, 100), manager=manager)
alignment_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((10, 60), (200, 20)), text='Alignment Radius', manager=manager)

cohesion_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((10, 130), (200, 30)), start_value=COHESION_RADIUS, value_range=(10, 100), manager=manager)
cohesion_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((10, 110), (200, 20)), text='Cohesion Radius', manager=manager)

speed_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((10, 180), (200, 30)), start_value=MAX_SPEED, value_range=(1, 10), manager=manager)
speed_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((10, 160), (200, 20)), text='Max Speed', manager=manager)

force_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((10, 230), (200, 30)), start_value=MAX_FORCE, value_range=(0.01, 1), manager=manager)
force_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((10, 210), (200, 20)), text='Max Force', manager=manager)

class Boid:
    def __init__(self):
        self.position = pygame.Vector2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        self.velocity = pygame.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        self.acceleration = pygame.Vector2(0, 0)
    
    def edges(self):
        """Wrap around the screen if the boid goes off the edges."""
        if self.position.x > WIDTH: self.position.x = 0
        if self.position.x < 0: self.position.x = WIDTH
        if self.position.y > HEIGHT: self.position.y = 0
        if self.position.y < 0: self.position.y = HEIGHT
    
    def apply_force(self, force):
        """Apply a force to the boid (affecting acceleration)."""
        self.acceleration += force
    
    def update(self):
        """Update position, velocity, and reset acceleration."""
        self.velocity += self.acceleration
        self.velocity = self.velocity.normalize() * min(MAX_SPEED, self.velocity.length())
        self.position += self.velocity
        self.acceleration *= 0
    
    def separation(self, boids):
        """Rule 1: Separation - steer to avoid crowding local flockmates."""
        steer = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            distance = self.position.distance_to(other.position)
            if other != self and distance < SEPARATION_RADIUS:
                diff = self.position - other.position
                diff /= distance
                steer += diff
                total += 1
        if total > 0:
            steer /= total
            if steer.length() > 0:
                steer = steer.normalize() * MAX_SPEED - self.velocity
                steer = steer.normalize() * min(MAX_FORCE, steer.length())
        return steer

    def alignment(self, boids):
        """Rule 2: Alignment - steer towards the average heading of local flockmates."""
        avg_velocity = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            if other != self and self.position.distance_to(other.position) < ALIGNMENT_RADIUS:
                avg_velocity += other.velocity
                total += 1
        if total > 0:
            avg_velocity /= total
            avg_velocity = avg_velocity.normalize() * MAX_SPEED
            steer = avg_velocity - self.velocity
            steer = steer.normalize() * min(MAX_FORCE, steer.length())
            return steer
        return pygame.Vector2(0, 0)
    
    def cohesion(self, boids):
        """Rule 3: Cohesion - steer to move toward the average position of local flockmates."""
        center_of_mass = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            if other != self and self.position.distance_to(other.position) < COHESION_RADIUS:
                center_of_mass += other.position
                total += 1
        if total > 0:
            center_of_mass /= total
            desired = center_of_mass - self.position
            if desired.length() > 0:
                desired = desired.normalize() * MAX_SPEED
                steer = desired - self.velocity
                steer = steer.normalize() * min(MAX_FORCE, steer.length())
                return steer
        return pygame.Vector2(0, 0)
    
    def flock(self, boids):
        """Apply the three flocking behaviors: separation, alignment, cohesion."""
        separation_force = self.separation(boids)
        alignment_force = self.alignment(boids)
        cohesion_force = self.cohesion(boids)
        
        # Adjust weightings of each behavior (tweak these values)
        self.apply_force(separation_force * 1.5)
        self.apply_force(alignment_force)
        self.apply_force(cohesion_force)

def main():
    global SEPARATION_RADIUS, ALIGNMENT_RADIUS, COHESION_RADIUS, MAX_SPEED, MAX_FORCE

    boids = [Boid() for _ in range(NUM_BOIDS)]
    
    running = True
    while running:
        time_delta = clock.tick(60)/1000.0
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.process_events(event)

        manager.update(time_delta)

        # Update sliders and the parameters
        SEPARATION_RADIUS = separation_slider.get_current_value()
        ALIGNMENT_RADIUS = alignment_slider.get_current_value()
        COHESION_RADIUS = cohesion_slider.get_current_value()
        MAX_SPEED = speed_slider.get_current_value()
        MAX_FORCE = force_slider.get_current_value()

        for boid in boids:
            boid.edges()
            boid.flock(boids)
            boid.update()
            pygame.draw.circle(screen, WHITE, (int(boid.position.x), int(boid.position.y)), 3)

        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
