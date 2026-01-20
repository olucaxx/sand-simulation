import pygame
import numpy as np
import sys
from colorsys import hsv_to_rgb
import random

# config
WIDTH = 100
HEIGHT = 50
SCALE = 10
FPS = 60

# init 
pygame.init()
pygame.display.set_caption("sand simulation")
screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))
clock = pygame.time.Clock()

# memoria da tela, onde os pixeis ficam armazenados, -1 = vazio e entre 0 e 360 = cor hue
world = np.full(shape=(HEIGHT, WIDTH), fill_value=-1)

# lookup table para armazenar os valores rgb do hue
LUT = np.zeros((361,3), dtype=np.uint8)
for hue in range(361):
    (r, g, b) = hsv_to_rgb(hue/360, 1, 1)
    LUT[hue] = (r*255, g*255, b*255)

hue_value = 0 # armazenar qual "posicao" do hue estamos
noise = 0.0

running = True
pressing = False

while running:        
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
                hue_value+=1

    if hue_value > 360: # garante o loop da roda de cores
        hue_value = 0

    # - MOVIMENTAR AREIA
    # fazemos um scan geral, de baixo para cima, da direita para a esquerda
    for y in range(HEIGHT-2, -1, -1):
        for x in range(0, WIDTH):
            if world[y, x] < 0: # verifica se o espaco atual esta vazio
                continue
            
            if world[y+1, x] < 0: # desce a areia de cima 
                world[y+1, x] = world[y, x]
                world[y, x] = -1
                continue
            
            noise += random.uniform(-0.05, 0.05) 
            noise = np.clip(noise, -1, 1) 

            if noise < 0: 
                if x+1 < WIDTH: # evita tentar colocar no espaco WIDTH + 1, gera index error
                    if world[y+1, x+1] < 0: # joga para a direita a areia
                        world[y+1, x+1] = world[y, x]
                        world[y, x] = -1
                        continue
            
            if x-1 >= 0: # nao permite colocar no -1 e evita um loop
                if world[y+1, x-1] < 0: # joga para a esquerda a areia
                    world[y+1, x-1] = world[y, x]
                    world[y, x] = -1
                    continue

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
