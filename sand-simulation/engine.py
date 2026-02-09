import pygame
import numpy as np
import sys
from colorsys import hsv_to_rgb
import random

# config
WIDTH = 150
HEIGHT = 200
SCALE = 3
FPS = 60
TICK_STEP = 1 / 60 # duracao de um tick (update da areia) ~16ms, 60 ticks por seg

GRAVITY = 0.15

# memoria da tela, onde as cores dos pixeis ficam armazenados, -1 = preto, 0-360 = hue
world = np.full(shape=(HEIGHT, WIDTH), fill_value=-1)

# velocidade queda de cada areia
vel = np.full(shape=(HEIGHT, WIDTH), fill_value=0.0)

# criacao de um surface para renderizacao da areia
world_surface = pygame.Surface((WIDTH, HEIGHT))

# cria um set para cada y, vamos armazenar os x dentro desses sets
active_xs_per_y = [set() for _ in range(HEIGHT-1)] 
# utilizado para melhorar a logica de queda da areia

# armazenamento das posicoes que sofreram atualizacao, tanto entrada quanto saida de areia
volatile_pixels = set()

# lookup table para armazenar os valores rgb do hue
LUT = np.zeros((361,3), dtype=np.uint8)
for hue in range(361):
    (r, g, b) = hsv_to_rgb(hue/360, 1, 1)
    LUT[hue] = (r*255, g*255, b*255)

hue_value = 0 

running = True
pressing = False
timer = 0.0
total_sand = 0
active_sand = 0

# init 
pygame.init()
pygame.display.set_caption("sand simulation")
screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

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
            for py in (-1, 0, 1):
                for px in (-1, 0, 1):
                    cx = cursor_x + px
                    cy = cursor_y + py

                    if 0 <= cx < WIDTH and 0 <= cy < HEIGHT:
                        if world[cy, cx] < 0:
                            vel[cy, cx] = 1
                            world[cy, cx] = hue_value

                            volatile_pixels.add((cx, cy)) 
                            # necessario garantir que o pixel colocado seja exibido no chao tambem

                            if cy < HEIGHT - 1:
                                active_xs_per_y[cy].add(cx)

            if hue_value >= 360: # garante o loop da roda de cores hue_value = 0
                hue_value = 0

            hue_value +=1
            

    # - MOVIMENTAR AREIA
    if timer >= TICK_STEP:
        for y in range(HEIGHT-2, -1, -1):
            xs_to_process = list(active_xs_per_y[y])
            
            for x in xs_to_process:
                volatile_pixels.add((x, y)) # garante a atualizacao na tela daquele pixel, mesmo que nao se mova

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
                
                volatile_pixels.add((new_x, new_y))

        total_sand = np.count_nonzero(world >= 0)
        active_sand = sum(len(s) for s in active_xs_per_y)

        timer -= TICK_STEP

    # - RENDER WORLD

    # atraves do surfarray vamos acessar o que esta armazenado
    surface_pixels = pygame.surfarray.pixels3d(world_surface)
    for x, y in volatile_pixels:
        if world[y, x] < 0:
            surface_pixels[x, y] = (0,0,0)
        if world[y, x] >= 0:
            surface_pixels[x, y] = LUT[world[y, x]]

    # precisamos liberar essa variavel para nao ocorrer problemas
    del surface_pixels
    # limpamos a lista, pois esses pixeis ja se "moveram"
    volatile_pixels.clear()

    # necessario para escalar a imagem para o tamanho da tela
    scaled_surface = pygame.transform.scale_by(world_surface, SCALE)
    
    screen.blit(scaled_surface, (0,0))

    total_text = font.render(f"areia total: {total_sand}", True, (255, 255, 255))
    active_text = font.render(f"areia ativa: {active_sand}", True, (255, 255, 255))
    screen.blit(total_text, (10, 10))
    screen.blit(active_text, (10, 10 + total_text.get_height() + 5))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
