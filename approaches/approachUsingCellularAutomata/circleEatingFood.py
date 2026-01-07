import pygame
import math
import random

pygame.init()
screen = pygame.display.set_mode((500,500))
clock = pygame.time.Clock()
running = True
dt = 0
j=0

agent1_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

def foodgen(j):
    for i in range(0,j):
        pygame.draw.circle(screen,"red",pygame.Vector2(random.randint(0, 500),random.randint(0, 500)),5)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False



    pygame.draw.circle(screen, (100,150,255), agent1_pos, 30)

    agent1_pos.x += random.choice([-1,0,1])
    agent1_pos.y += random.choice([-1,0,1])

    if(random.randint(0,150)==15):
        j+=1

    foodgen(j)

    pygame.display.flip()
    screen.fill((0,0,0))

    dt = clock.tick(60) / 10
    print()

pygame.quit()