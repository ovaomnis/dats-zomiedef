import pygame
import time
from api import fetchUnits
from datetime import datetime

pygame.init()

# Game data
units_on_field = None

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
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
cyan = (0, 255, 255)
background_color = (0, 0, 0)
black = (0, 0, 0)

# PyGame Code
pygame.display.set_caption("Pygame Example: Movement")

# Step Code
def step():
    global last_send_sec
    global units_on_field

    current = datetime.now().second
    if not (abs(current - start_sec) % 2 == 0 and last_send_sec != current):
        return
    
    units_on_field = fetchUnits()
    # print(units_on_field['base'])


def draw_base(surface: pygame.Surface):
    if not units_on_field:
        return
    
    for base in units_on_field['base']:
        base_y = scale * base['x']
        base_x = scale * base['y']
        if base['isHead']:
            base_color = blue
        else:
            base_color = cyan
        pygame.draw.rect(surface, blue, (base_x, base_y, scale, scale), 2)
        # print((base_x, base_y, base_x + scale, base_y + scale))
    # print() 



def get_field():
    size = (FIELD_WIDTH, FIELD_HEIGHT)
    field = pygame.Surface(size=size, flags=0)
    field.fill(white)

    draw_base(field)

    # Draw lines
    # for i in range(0, size[0], scale):
    #     pygame.draw.line(field, "#e3e3e3", [i, 0], [i, size[1]])

    # for i in range(0, size[1], scale):
    #     pygame.draw.line(field, "#e3e3e3", [0, i], [size[0], i])

    # draw_base(field)

    return field


# def get_minimap():
#     size = (FIELD_WIDTH / scale * minimap_scale, FIELD_HEIGHT / scale * minimap_scale)
#     view_size = (
#         screen_width / scale * minimap_scale,
#         screen_height / scale * minimap_scale,
#     )
#     minimap = pygame.Surface(size=size, flags=pygame.SRCALPHA)
#     minimap.fill((*white, 200))
#     pygame.draw.rect(minimap, (*black, 100), (0, 0, *size), 1)
#     pygame.draw.rect(
#         minimap,
#         red,
#         (
#             -field_x_offset / scale * minimap_scale,
#             -field_y_offset / scale * minimap_scale,
#             *(view_size),
#         ),
#         1,
#     )

#     return minimap


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

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(background_color)
    field = get_field()
    # minimap = get_minimap()

    screen.blit(field, (field_x_offset, field_y_offset))
    # screen.blit(minimap, (0, 0))

    pygame.display.update()

    clock.tick(20)

pygame.quit()
