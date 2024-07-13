from dataclasses import dataclass
from typing import List, Tuple
import pygame
import time
from api import fetchUnits, fetchWorld, postCommands
from datetime import datetime
from colors import Colors
import math
import random

from fonts import Fonts
from utils import get_distance

pygame.init()

# Game data
units_on_field = {}
commands_to_execute = {"attack": [], "build": [], "moveBase": {}}
target_priority = "zombie"
dots = []

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

# Step variables
last_send_sec = 0
start_sec = 0

# UI Layout
ui_layer = pygame.Surface([screen_width, screen_height], pygame.SRCALPHA)
base_range = []

# PyGame Code
pygame.display.set_caption("ZomPy")


# Find enemies
def toggle_target():
    global target_priority
    if target_priority == "enemy":
        target_priority = "zombie"
    else:
        target_priority = "enemy"


def generate_points_within_radius(main_point: Tuple[int, int], radius: int):
    points = []
    x_center, y_center = main_point
    for x in range(x_center - radius, x_center + radius + 1):
        for y in range(y_center - radius, y_center + radius + 1):
            if (x - x_center) ** 2 + (y - y_center) ** 2 <= radius**2:
                points.append((x, y))
    return points


def generate_radius_area(bases: List[dict]):
    global base_range
    base_range = []
    points = []
    for base in bases:
        points.extend(
            generate_points_within_radius(
                main_point=(base.get("x"), base.get("y")), radius=base.get("range")
            )
        )
    base_range.extend(set(points))


def predict_next_zombie_cords(zombie: dict) -> Tuple[int, int]:
    if zombie.get("waitTurns") < 1:
        return zombie.get("x"), zombie.get("y")

    target_x = 0
    target_y = 0
    # print(zombie.get('type'), f"{zombie.get('x')}, {zombie.get('y')}", zombie.get('direction'))

    if zombie.get("type") == "chaos_knight":
        match zombie.get("direction"):
            case "up":
                target_x, target_y = (
                    zombie.get("x") + random.choice([1, -1]),
                    zombie.get("y") + 2,
                )
            case "down":
                target_x, target_y = (
                    zombie.get("x") + random.choice([1, -1]),
                    zombie.get("y") - 2,
                )
            case "right":
                target_x, target_y = zombie.get("x") + 2, zombie.get(
                    "y"
                ) + random.choice([1, -1])
            case "left":
                target_x, target_y = zombie.get("x") - 2, zombie.get(
                    "y"
                ) + random.choice([1, -1])
        return target_x, target_y

    match zombie.get("direction"):
        case "up":
            target_x, target_y = zombie.get("x"), zombie.get("y") + zombie.get("speed")
        case "down":
            target_x, target_y = zombie.get("x"), zombie.get("y") - zombie.get("speed")
        case "right":
            target_x, target_y = zombie.get("x") + zombie.get("speed"), zombie.get("y")
        case "left":
            target_x, target_y = zombie.get("x") - zombie.get("speed"), zombie.get("y")
    # print(target_x, target_y)
    # print()
    return target_x, target_y


def find_targets(z: List[dict] | None, e: List[dict] | None, b: List[dict] | None):
    # print("==============\nStarted Scanning Targets\n==============")
    attack_list = []
    enemies = e.copy() if e else []
    zombies = z.copy() if z else []
    bases = b.copy() if b else []

    # print("Bases:", bases)
    for base in bases:
        base_x = base.get("x")
        base_y = base.get("y")
        range = base.get("range")
        founded_enemy_targets = []
        founded_zombie_targets = []
        # print(base)

        for enem in enemies:
            target_x, target_y = enem.get("x"), enem.get("y")
            distance = get_distance(target_x, target_y, base_x, base_y)
            if distance <= range:
                founded_enemy_targets.append(
                    {"unit": enem, "target": {"x": target_x, "y": target_y}}
                )

        founded_enemy_targets = sorted(
            founded_enemy_targets, key=lambda t: t["unit"]["health"]
        )
        # print('\nFounded enemy targets:')
        # for target in founded_enemy_targets:
        #     print("health:", target['unit']['health'])
        #     print("cords:", target['target'])

        for zombie in zombies:
            target_x, target_y = predict_next_zombie_cords(zombie)
            distance = get_distance(target_x, target_y, base_x, base_y)
            if distance <= range:
                founded_zombie_targets.append(
                    {"unit": zombie, "target": {"x": target_x, "y": target_y}}
                )

        founded_zombie_targets = sorted(
            founded_zombie_targets, key=lambda t: t["unit"]["health"]
        )
        # print('\nFounded zombie targets:')
        # for target in founded_zombie_targets:
        #     print("health:", target['unit']['health'])
        #     print("cords:", target['target'])

        match target_priority:
            case "enemy":
                if founded_enemy_targets:
                    target = founded_enemy_targets[0]
                    attack_list.append(
                        {"blockId": base.get("id"), "target": target["target"]}
                    )
                    if target["unit"]["health"] - base.get("attack") <= 0:
                        # print('found target', target)
                        enemies.remove(target["unit"])
                    continue

                if founded_zombie_targets:
                    target = founded_zombie_targets[0]
                    attack_list.append(
                        {"blockId": base.get("id"), "target": target["target"]}
                    )
                    if target["unit"]["health"] - base.get("attack") <= 0:
                        # print('found target', target)
                        zombies.remove(target["unit"])
                    continue
            case "zombie":
                if founded_zombie_targets:
                    target = founded_zombie_targets[0]
                    attack_list.append(
                        {"blockId": base.get("id"), "target": target["target"]}
                    )
                    if target["unit"]["health"] - base.get("attack") <= 0:
                        # print('found target', target)
                        zombies.remove(target["unit"])
                    continue
                if founded_enemy_targets:
                    target = founded_enemy_targets[0]
                    attack_list.append(
                        {"blockId": base.get("id"), "target": target["target"]}
                    )
                    if target["unit"]["health"] - base.get("attack") <= 0:
                        # print('found target', target)
                        enemies.remove(target["unit"])
                    continue

    return attack_list


# Step Code
def step():
    global last_send_sec
    global units_on_field
    global commands_to_execute
    global dots

    current = datetime.now().second
    if not (abs(current - start_sec) % 2 == 0 and last_send_sec != current):
        return

    commands_to_execute = {"attack": [], "build": [], "moveBase": {}}

    units = fetchUnits()
    if units:
        units_on_field = units
        last_send_sec = current

    # print(units_on_field.get('enemyBlocks'))
    # enemies = find_enemis([
    #     *(units_on_field.get('zombies') if units_on_field.get('zombies') else []),
    #     *(units_on_field.get('enemyBlocks') if units_on_field.get('enemyBlocks') else [])
    # ], units_on_field.get('base', []))
    # if units_on_field:
    #     enemies = find_targets(
    #         units_on_field.get("zombies"),
    #         units_on_field.get("enemyBlocks"),
    #         units_on_field.get("base"),
    #     )
    #     # print(enemies)
    #     commands_to_execute["attack"] = enemies
    #     generate_radius_area(units_on_field.get("base"))
    #     postCommands(commands_to_execute)
    
    
    # print(commands_to_execute)

    # print(units_on_field)
    # print(units_on_field['base'])


def build_base(cords: Tuple[int, int]):
    global commands_to_execute
    new_x = math.floor((cords[0] - field_x_offset) / scale)
    new_y = math.floor((cords[1] - field_y_offset) / scale)
    commands_to_execute["build"].append({"x": new_x, "y": new_y})
    print({"x": new_x, "y": new_y})


def find_base():
    global field_x_offset
    global field_y_offset

    if not units_on_field or not units_on_field.get("base"):
        return

    head = list(filter(lambda base: base.get("isHead"), units_on_field["base"]))
    if head:
        field_x_offset = -head[0]["x"] * scale + screen_width / 2
        field_y_offset = -head[0]["y"] * scale + screen_height / 2


# Draw units
def draw_base(surface: pygame.Surface):
    if not units_on_field != {} or not units_on_field.get("base"):
        return

    for base in units_on_field["base"]:
        health_in_percentage = (
            (base.get("health", 300) / 300)
            if base.get("isHead", False)
            else (base.get("health", 100) / 100)
        )
        base_x = scale * base["x"] + field_x_offset
        base_y = scale * base["y"] + field_y_offset
        base_color = Colors.base_head if base.get("isHead", False) else Colors.base
        base_surface = pygame.Surface((scale, scale), pygame.SRCALPHA)
        pygame.draw.rect(base_surface, (*base_color, 100), (0, 0, scale, scale))
        pygame.draw.rect(
            base_surface, base_color, (0, 0, scale * health_in_percentage, scale)
        )
        pygame.draw.rect(base_surface, base_color, (0, 0, scale, scale), 1)
        surface.blit(base_surface, (base_x, base_y))
        # print("Base drawn")
        # pygame.draw.rect(surface, base_color, (base_x, base_y, scale, scale))
        # print((base_x, base_y, scale, scale))
    # print("---")
    # print()


def draw_zombies(surface: pygame.Surface):
    if not units_on_field != {} or not units_on_field.get("zombies"):
        return

    for zomb in units_on_field["zombies"]:
        zomb_x = scale * zomb["x"] + field_x_offset
        zomb_y = scale * zomb["y"] + field_y_offset
        # print(zomb['x'], zomb['y'])
        pygame.draw.rect(surface, Colors.zomb, (zomb_x, zomb_y, scale, scale))


def draw_enemies(surface: pygame.Surface):
    if not units_on_field != {} or not units_on_field.get("enemyBlocks"):
        return

    for enem in units_on_field["enemyBlocks"]:
        enem_x = scale * enem["x"] + field_x_offset
        enem_y = scale * enem["y"] + field_y_offset
        enem_color = Colors.enemy_head if enem.get("isHead", False) else Colors.enemy

        pygame.draw.rect(surface, enem_color, (enem_x, enem_y, scale, scale))


def draw_zpots(surface: pygame.Surface):
    if not dots:
        return

    for zpot in dots:
        zpot_x = scale * zpot["x"] + field_x_offset
        zpot_y = scale * zpot["y"] + field_y_offset
        pygame.draw.rect(surface, (0, 0, 0), (zpot_x, zpot_y, scale, scale))


def draw_targets(surface: pygame.Surface):
    # print(commands_to_execute)
    for target in commands_to_execute["attack"]:
        x = scale * target["target"]["x"] + field_x_offset
        y = scale * target["target"]["y"] + field_y_offset
        pygame.draw.line(
            surface, Colors.red, (x + scale / 2, y), (x + scale / 2, y + scale)
        )
        pygame.draw.line(
            surface, Colors.red, (x, y + scale / 2), (x + scale, y + scale / 2)
        )
        pygame.draw.circle(
            surface, Colors.red, (x + scale / 2, y + scale / 2), scale / 2 - 2, 1
        )


# Draw UI
def draw_stats(surface: pygame.Surface):
    priority_text_stat = Fonts.sm.render(
        f"priority: {target_priority}", True, Colors.black
    )
    surface.blit(priority_text_stat, (20, 20))

    if units_on_field and units_on_field.get("player"):
        gold_text_stat = Fonts.sm.render(
            f"gold: {units_on_field['player']['gold']}", True, Colors.black
        )
        points_text_stat = Fonts.sm.render(
            f"points: {units_on_field['player']['points']}", True, Colors.black
        )
        zombie_kills = Fonts.sm.render(
            f"zombie kills: {units_on_field['player']['zombieKills']}",
            True,
            Colors.black,
        )
        enemy_block_kils = Fonts.sm.render(
            f"enemy kills: {units_on_field['player']['enemyBlockKills']}",
            True,
            Colors.black,
        )

        surface.blit(gold_text_stat, (20, 40))
        surface.blits(
            (
                (
                    gold_text_stat,
                    (20, 40),
                ),
                (
                    points_text_stat,
                    (20, 60),
                ),
                (
                    zombie_kills,
                    (20, 80),
                ),
                (
                    enemy_block_kils,
                    (20, 100),
                ),
            )
        )

def draw_range(surface: pygame.Surface):
    for point in base_range:
        x = scale * point[0] + field_x_offset
        y = scale * point[1] + field_y_offset
        range = pygame.Surface((scale, scale), pygame.SRCALPHA)
        range.fill((*Colors.blue, 100))
        surface.blit(range, (x, y))


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

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                build_base(event.pos)
                pygame.display.update()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                find_base()
            elif event.key == pygame.K_t:
                toggle_target()

    # print(Colors.white)
    screen.fill(Colors.white)
    ui_layer.fill((*Colors.white, 0))
    # Render Units
    draw_zpots(screen)
    draw_base(screen)
    draw_zombies(screen)
    draw_enemies(screen)
    draw_targets(screen)

    # Render UI
    draw_stats(ui_layer)
    draw_range(ui_layer)
    screen.blit(ui_layer, (0, 0))
    pygame.display.update()

    clock.tick(20)

pygame.quit()
