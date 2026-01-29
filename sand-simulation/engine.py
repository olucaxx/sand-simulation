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

# velocidade de cada areia
vel = np.full(shape=(HEIGHT, WIDTH), fill_value=0.0)

# cria um set para cada y, vamos armazenar os x dentro desses sets
active_xs_per_y = [set() for _ in range(HEIGHT-1)] 
# utilizado para melhorar a renderizacao

# lookup table para armazenar os valores rgb do hue
LUT = np.zeros((361,3), dtype=np.uint8)
for hue in range(361):
    (r, g, b) = hsv_to_rgb(hue/360, 1, 1)
    LUT[hue] = (r*255, g*255, b*255)

hue_value = 0 # armazenar qual "posicao" do hue estamos

gravity = 0.15

running = True
pressing = False
timer = 0.0

def update_active_sand(new_y, new_x, y, x):
    active_xs_per_y[y].discard(x)

    if new_y < HEIGHT-1:
        active_xs_per_y[new_y].add(new_x)

def wake_neighbors(y, x):
    for nx in (x-1, x, x+1):
        # acorda os vizinhos em volta desse espaco
        if 0 <= nx < WIDTH and y > 0 and world[y, nx] >= 0:
            active_xs_per_y[y-1].add(nx)

def fall_down(y, x):
    world[y+1, x] = world[y, x]
    vel[y+1, x] = vel[y, x]
    world[y, x] = -1
    vel[y, x] = 0
    update_active_sand(y+1, x, y, x)
    wake_neighbors(y+1, x)

def fall_right(y, x):
    world[y+1, x+1] = world[y, x]
    vel[y+1, x+1] = vel[y, x]
    world[y, x] = -1
    vel[y, x] = 0
    update_active_sand(y+1, x+1, y, x)
    wake_neighbors(y+1, x+1)

def fall_left(y, x):
    world[y+1, x-1] = world[y, x]
    vel[y+1, x-1] = vel[y, x]
    world[y, x] = -1
    vel[y, x] = 0
    update_active_sand(y+1, x-1, y, x) 
    wake_neighbors(y+1, x-1)

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

    world_x = mouse_x // SCALE
    world_y = mouse_y // SCALE

    # - COLOCAR AREIA
    if pressing:                                           # apertando
        if 0 <= world_x < WIDTH and 0 <= world_y < HEIGHT: # dentro da tela
             if world[world_y, world_x] < 0:               # espaco esta vazio
                vel[world_y, world_x] = 1
                world[world_y, world_x] = hue_value
                if world_y < HEIGHT-1 and world_x < WIDTH:
                    active_xs_per_y[world_y].add(world_x)    
                hue_value+=1

    if hue_value > 360: # garante o loop da roda de cores
        hue_value = 0

    # - MOVIMENTAR AREIA
    if timer >= TICK_STEP:
        print(active_xs_per_y)
        # fazemos um scan geral, de baixo para cima
        for y in range(HEIGHT-2, -1, -1):
            # criamos uma copia para iteracao
            xs_to_process = list(active_xs_per_y[y])
            
            for x in xs_to_process:
                # remove do set se a areia ja se moveu em outro step
                if world[y, x] < 0:
                    active_xs_per_y[y].discard(x)
                    continue
                
                vel[y, x] += gravity
                steps = int(vel[y, x])
                
                if steps <= 0:
                    active_xs_per_y[y].discard(x)
                    continue
                
                # movimento relizado em steps sequenciais
                current_y = y
                current_x = x
                steps_taken = 0

                # simulacao de movimento continuo
                while steps_taken < steps and current_y < HEIGHT-1:
                    if world[current_y + 1, current_x] < 0:
                        fall_down(current_y, current_x)
                        current_y += 1
                        steps_taken += 1
                        continue
                    
                    moved = False
                    dirs = [-1, 1]
                    # randomiza esquerda/direita para evitar vies estrutural no monte
                    random.shuffle(dirs)
                    
                    for dx in dirs:
                        if dx == -1 and current_x > 0:
                            if world[current_y + 1, current_x - 1] < 0:
                                fall_left(current_y, current_x)
                                current_y += 1
                                current_x -= 1
                                steps_taken += 1
                                moved = True
                                break
                        elif dx == 1 and current_x < WIDTH - 1:
                            if world[current_y + 1, current_x + 1] < 0:
                                fall_right(current_y, current_x)
                                current_y += 1
                                current_x += 1
                                steps_taken += 1
                                moved = True
                                break
                    
                    if not moved:
                        vel[current_y, current_x] *= 0.5
                        if vel[current_y, current_x] < 0.5:
                            vel[current_y, current_x] = 0
                        # acorda vizinhos acima que podem ter perdido suporte
                        wake_neighbors(current_y, current_x)
                        break
                
                if steps_taken == steps and current_y < HEIGHT - 1:
                    # garante que particulas que ainda tem energia continuem ativas no proximo tick
                    vel[current_y, current_x] = max(vel[current_y, current_x], 0.1)
        
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
