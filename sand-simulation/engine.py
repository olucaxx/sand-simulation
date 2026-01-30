import pygame
import numpy as np
import sys
from colorsys import hsv_to_rgb
import random

# config
WIDTH = 50
HEIGHT = 100
SCALE = 8
FPS = 60
TICK_STEP = 1 / 60 # duracao de um tick (update da areia) ~16ms, 60 ticks por seg

GRAVITY = 0.15

# memoria da tela, onde as cores dos pixeis ficam armazenados, -1 = preto, 0-360 = hue
world = np.full(shape=(HEIGHT, WIDTH), fill_value=-1)

# velocidade queda de cada areia
vel = np.full(shape=(HEIGHT, WIDTH), fill_value=0.0)

# cria um set para cada y, vamos armazenar os x dentro desses sets
active_xs_per_y = [set() for _ in range(HEIGHT-1)] 
# utilizado para melhorar a logica de queda da areia

# lookup table para armazenar os valores rgb do hue
LUT = np.zeros((361,3), dtype=np.uint8)
for hue in range(361):
    (r, g, b) = hsv_to_rgb(hue/360, 1, 1)
    LUT[hue] = (r*255, g*255, b*255)

hue_value = 0 

running = True
pressing = False
timer = 0.0

# init 
pygame.init()
pygame.display.set_caption("sand simulation")
screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))
clock = pygame.time.Clock()

while running:        
    dt = clock.tick(FPS) / 1000.0 # quanto tempo desde o ultimo loop
    timer += dt # tempo acumulado

    # - EVENTOS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pressing = True

        if event.type == pygame.MOUSEBUTTONUP:
            pressing = False

    # - POSICAO MOUSE
    mouse_x, mouse_y = pygame.mouse.get_pos()

    cursor_x = mouse_x // SCALE
    cursor_y = mouse_y // SCALE

    # - COLOCAR AREIA
    if pressing:               
        if 0 <= cursor_x < WIDTH and 0 <= cursor_y < HEIGHT: 
            if world[cursor_y, cursor_x] < 0: 
                vel[cursor_y, cursor_x] = 1
                world[cursor_y, cursor_x] = hue_value

                if cursor_y < HEIGHT-1:
                    active_xs_per_y[cursor_y].add(cursor_x)    

                if hue_value >= 360: # garante o loop da roda de cores
                    hue_value = 0       
                    
                hue_value+=1

    # - MOVIMENTAR AREIA
    if timer >= TICK_STEP:
        for y in range(HEIGHT-2, -1, -1):
            xs_to_process = list(active_xs_per_y[y])
            
            for x in xs_to_process:
                if world[y, x] < 0:
                    active_xs_per_y[y].discard(x)
                    continue
                
                vel[y, x] += GRAVITY
                
                steps_to_move = int(vel[y, x])
                
                max_steps_per_frame = 5
                if steps_to_move > max_steps_per_frame:
                    steps_to_move = max_steps_per_frame
                    vel[y, x] = max_steps_per_frame
                
                if steps_to_move <= 0:
                    if vel[y, x] < 0.1:
                        active_xs_per_y[y].discard(x)
                    continue
                
                original_hue = world[y, x]
                original_vel = vel[y, x]
                
                new_y = y
                new_x = x
                steps_taken = 0
                
                for step in range(steps_to_move):
                    if new_y >= HEIGHT - 1:
                        break
                    
                    if world[new_y + 1, new_x] < 0:
                        new_y += 1
                        steps_taken += 1
                        continue
                    
                    moved = False
                    directions = [-1, 1]
                    random.shuffle(directions)
                    
                    for dx in directions:
                        next_x = new_x + dx
                        if 0 <= next_x < WIDTH and world[new_y + 1, next_x] < 0:
                            new_y += 1
                            new_x = next_x
                            steps_taken += 1
                            moved = True
                            original_vel = max(int(original_vel * 0.7), 1)
                            break
                    
                    if not moved:
                        break
                
                if new_y == y and new_x == x:
                    active_xs_per_y[y].discard(x)
                    continue

                world[y, x] = -1
                vel[y, x] = 0
                
                world[new_y, new_x] = original_hue
                vel[new_y, new_x] = original_vel
                
                active_xs_per_y[y].discard(x)
                
                if new_y < HEIGHT - 1 and vel[new_y, new_x] > 0.1:
                    active_xs_per_y[new_y].add(new_x)
                
                if new_y > 0:
                    for nx in (new_x-1, new_x, new_x+1):
                        if 0 <= nx < WIDTH and world[new_y-1, nx] >= 0:
                            active_xs_per_y[new_y-1].add(nx)
                
                if y > 0:
                    for nx in (x-1, x, x+1):
                        if 0 <= nx < WIDTH and world[y-1, nx] >= 0:
                            active_xs_per_y[y-1].add(nx)

        timer -= TICK_STEP

    # - RENDER WORLD
    screen.fill((0,0,0)) # pinta toda a SCREEN nao o world

    pixel_y, pixel_x = np.where(world >= 0)
    pixels = list(zip(pixel_y, pixel_x))

    for y, x in pixels:
        pygame.draw.rect(
                    screen, 
                    LUT[world[y, x]], 
                    (x * SCALE, y * SCALE, SCALE, SCALE)
                )

    # - RENDER POSICAO DO MOUSE
    if 0 <= cursor_x < WIDTH and 0 <= cursor_y < HEIGHT:
        pygame.draw.rect(
            screen,
            LUT[hue_value],
            (cursor_x * SCALE, cursor_y * SCALE, SCALE, SCALE)
        )

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
