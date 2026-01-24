import pygame
import numpy as np
import sys
from colorsys import hsv_to_rgb
import random

# config
WIDTH = 50
HEIGHT = 100
SCALE = 5
FPS = 60
TICK_STEP = 1 / 60 # duracao de um tick (update da areia) ~16ms, 60 ticks por seg

# memoria da tela, onde os pixeis ficam armazenados, -1 = vazio e entre 0 e 360 = cor hue
world = np.full(shape=(HEIGHT, WIDTH), fill_value=-1)

# cria um set para cada y, vamos armazenar os x dentro desses sets
active_xs_per_y = [set() for _ in range(HEIGHT-1)] 
# utilizado para melhorar a renderizacao

# lookup table para armazenar os valores rgb do hue
LUT = np.zeros((361,3), dtype=np.uint8)
for hue in range(361):
    (r, g, b) = hsv_to_rgb(hue/360, 1, 1)
    LUT[hue] = (r*255, g*255, b*255)

hue_value = 0 # armazenar qual "posicao" do hue estamos
noise = 0.0

running = True
pressing = False
timer = 0.0

def update_active_sand(new_y, new_x, y, x):
    active_xs_per_y[y].discard(x)

    if new_y < HEIGHT-1:
        active_xs_per_y[new_y].add(new_x)

# init 
pygame.init()
pygame.display.set_caption("sand simulation")
screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))
clock = pygame.time.Clock()

while running:        
    print(list(active_xs_per_y))
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

    world_x = mouse_x // SCALE
    world_y = mouse_y // SCALE

    # - COLOCAR AREIA
    if pressing:                                           # apertando
        if 0 <= world_x < WIDTH and 0 <= world_y < HEIGHT: # dentro da tela
             if world[world_y, world_x] < 0:               # espaco esta vazio
                world[world_y, world_x] = hue_value
                if world_y < HEIGHT-1 and world_x < WIDTH-1:
                    active_xs_per_y[world_y].add(world_x)
                hue_value+=1

    if hue_value > 360: # garante o loop da roda de cores
        hue_value = 0

    # - MOVIMENTAR AREIA
    if timer >= TICK_STEP: # quer dizer que temos que pagar um tick
        # fazemos um scan geral, de baixo para cima, da direita para a esquerda
        for y in range(HEIGHT-2, -1, -1):
            for x in list(active_xs_per_y[y]): # necessario criar copia do set, ele sera atualizado durante a iteracao
                can_down = (y+1 < HEIGHT and world[y+1, x] < 0)
                can_right = (y+1 < HEIGHT and x+1 < WIDTH and world[y+1, x+1] < 0)
                can_left = (y+1 < HEIGHT and x-1 >= 0 and world[y+1, x-1] < 0)

                noise += random.uniform(-0.05, 0.05) 
                noise = np.clip(noise, -1, 1) 

                if can_down:
                    world[y+1, x] = world[y, x]
                    world[y, x] = -1
                    update_active_sand(y+1, x, y, x)
                    continue
            
                if noise < 0:
                    if can_right: 
                        world[y+1, x+1] = world[y, x]
                        world[y, x] = -1
                        update_active_sand(y+1, x+1, y, x)
                        continue

                if can_left:
                    world[y+1, x-1] = world[y, x]
                    world[y, x] = -1
                    update_active_sand(y+1, x-1, y, x)
                    continue

                if can_right: 
                    world[y+1, x+1] = world[y, x]
                    world[y, x] = -1
                    update_active_sand(y+1, x+1, y, x)
                    continue

                if not(can_down or can_right or can_left):
                    active_xs_per_y[y].discard(x)


        timer -= TICK_STEP # desconta nosso gasto de update logico

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
    if 0 <= world_x < WIDTH and 0 <= world_y < HEIGHT:
        pygame.draw.rect(
            screen,
            LUT[hue_value],
            (world_x * SCALE, world_y * SCALE, SCALE, SCALE)
        )

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
