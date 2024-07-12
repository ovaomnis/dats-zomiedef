from dataclasses import dataclass
from typing import List
import pygame
import time
from api import fetchUnits, fetchWorld
from datetime import datetime
from enum import Enum

pygame.init()

# Game data
units_on_field = {}

# PyGame variables
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

# Field variables
scale = 20
minimap_scale = 2
field_x_offset = 0
field_y_offset = 0
field_x_offset_step = 5
field_y_offset_step = 5
FIELD_WIDTH = screen_width
FIELD_HEIGHT = screen_height

# Field Objects
objects = [
    [0, 0],
    [3, 0],
    [0, 3],
]

# Step variables
last_send_sec = 0
start_sec = 0

# Colors
class Colors:
    red = (255, 0, 0)
    green = (0, 255, 0)
    white = (255, 255, 255)
    blue = (0, 0, 255)
    cyan = (0, 255, 255)
    gray = (128, 128, 128)
    enemy = (49, 3, 255)
    enemy_head = (49, 3, 255)
    zomb = (93, 158, 43)
    base = (224, 152, 18)
    base_head = (224, 107, 18)
    background_color = (28, 0, 156)
    black = (0, 0, 0)

# PyGame Code
pygame.display.set_caption("Pygame Example: Movement")

def find_enemis(targets: List[dict], base: List[dict]):
    print(targets)
    print(base)

# Step Code
def step():
    global last_send_sec
    global units_on_field

    current = datetime.now().second
    if not (abs(current - start_sec) % 2 == 0 and last_send_sec != current):
        return
    
    units = fetchUnits()
    if units:
        units_on_field = units
    
    # print(units_on_field.get('enemyBlocks'))
    find_enemis([
        *(units_on_field.get('zombies') if units_on_field.get('zombies') else []),
        *(units_on_field.get('enemyBlocks') if units_on_field.get('enemyBlocks') else [])
    ], units_on_field.get('base', []))

    
    # print(units_on_field)
    # print(units_on_field['base'])


def draw_base(surface: pygame.Surface):
    if not units_on_field != {} or not units_on_field.get('base'):
        return
    
    for base in units_on_field['base']:
        base_x = scale * base['x'] + field_x_offset
        base_y = scale * base['y'] + field_y_offset
        base_color = Colors.base_head if base.get('isHead', False) else Colors.base
    
        pygame.draw.rect(surface, base_color, (base_x, base_y, scale, scale))
        # print((base_x, base_y, scale, scale))
    # print()

def draw_zombies(surface: pygame.Surface):
    if not units_on_field != {} or not units_on_field.get("zombies"):
        return
    
    for zomb in units_on_field['zombies']:
        zomb_x = scale * zomb['x'] + field_x_offset
        zomb_y = scale * zomb['y'] + field_y_offset
    
        pygame.draw.rect(surface, Colors.zomb, (zomb_x, zomb_y, scale, scale))

def draw_enemies(surface: pygame.Surface):
    if not units_on_field != {} or not units_on_field.get("enemyBlocks"):
        return
    
    for enem in units_on_field['enemyBlocks']:
        enem_x = scale * enem['x'] + field_x_offset
        enem_y = scale * enem['y'] + field_y_offset
        enem_color = Colors.enemy_head if enem.get('isHead', False) else Colors.enemy
    
        pygame.draw.rect(surface, enem_color, (enem_x, enem_y, scale, scale))


def find_base():
    global field_x_offset
    global field_y_offset

    if not units_on_field or not units_on_field.get('base'):
        return
    
    head = list(filter(lambda base: base.get('isHead'), units_on_field['base']))
    if head:
        field_x_offset = -head[0]['x'] * scale + screen_width/2
        field_y_offset = -head[0]['y'] * scale + screen_height/2


def draw_zpots(surface: pygame.Surface):
    world = fetchWorld()
    
    if not world or not world.get('zpots'):
        return
    
    for zpot in world['zpots']:
        zpot_x = scale * zpot['x'] + field_x_offset
        zpot_y = scale * zpot['y'] + field_y_offset
        pygame.draw.rect(surface, (0, 0, 0), (zpot_x, zpot_y, scale, scale))

draw_zpots(screen)

running = True
while running:
    step()
    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        field_y_offset += field_y_offset_step
        # print("pressed up", field_y_offset)
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        # print("pressed down", field_y_offset)
        field_y_offset -= field_y_offset_step
    if keys[pygame.K_LEFT] or keys[pygame.K_d]:
        field_x_offset += field_x_offset_step
        # print("pressed left", field_x_offset)
    if keys[pygame.K_RIGHT] or keys[pygame.K_a]:
        field_x_offset -= field_x_offset_step
        # print("pressed right", field_x_offset)
    if keys[pygame.K_t]:
        find_base()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # print(Colors.white)
    screen.fill(Colors.white)
    draw_base(screen)
    draw_zombies(screen)
    draw_enemies(screen)

    pygame.display.update()

    clock.tick(20)

pygame.quit()
