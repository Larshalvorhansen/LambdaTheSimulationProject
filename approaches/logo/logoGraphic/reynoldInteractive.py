import pygame
import random
import pygame_gui
import math

# Initialize Pygame and Pygame GUI
pygame.init()
pygame.display.set_caption('Boids Simulation with Background Interaction')
WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Pygame GUI manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Define colors
BLACK = (200, 200, 200)
WHITE = (100, 100, 100)

# Load background image (with transparency)
background_image = pygame.image.load('lambdaMedium.png').convert_alpha()
bg_width, bg_height = background_image.get_size()

# Calculate the position to center the image
bg_x = (WIDTH - bg_width) // 2
bg_y = (HEIGHT - bg_height) // 2

# Boid parameters (set initial values)
NUM_BOIDS = 500
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
        self.color = WHITE  # Default color is white
    
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
        if self.velocity.length() > 0:  # Check if velocity is non-zero before normalizing
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
                if steer.length() > 0:
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
            if avg_velocity.length() > 0:  # Check if avg_velocity is non-zero
                avg_velocity = avg_velocity.normalize() * MAX_SPEED
                steer = avg_velocity - self.velocity
                if steer.length() > 0:  # Check if steer is non-zero
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
                if steer.length() > 0:  # Check if steer is non-zero
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
    
    def interact_with_background(self, background, bg_x, bg_y, bg_width, bg_height):
        """Check if the boid is on an opaque part of the background image."""
        x, y = int(self.position.x - bg_x), int(self.position.y - bg_y)
        if 0 <= x < bg_width and 0 <= y < bg_height:
            pixel = background.get_at((x, y))
            # Check alpha channel (opacity) to see if boid overlaps with the image
            self.color = BLACK if pixel[3] != 0 else WHITE  # Change to black if overlapping
            if pixel[3] != 0:  # Check alpha channel (opacity)
                # Simple behavior: Stop the boid if it hits an opaque pixel
                self.velocity *= 0

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

        # Draw background image centered
        # screen.blit(background_image, (bg_x, bg_y))

        for boid in boids:
            boid.edges()
            boid.flock(boids)
            boid.update()
            boid.interact_with_background(background_image, bg_x, bg_y, bg_width, bg_height)
            # Draw the boid with its current color
            pygame.draw.circle(screen, boid.color, (int(boid.position.x), int(boid.position.y)), 5)

        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
