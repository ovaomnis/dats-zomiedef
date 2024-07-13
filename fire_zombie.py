import time

from requ import get_world, get_units, post_command


def predict_fire_coordinates(zombie):
    """Вычисляет координаты для атаки на упреждение в зависимости от типа и движения зомби, кроме 'chaos_knight'."""
    x, y, z_type, direction = zombie['x'], zombie['y'], zombie['type'], zombie.get('direction', '')
    predicted_positions = []

    if z_type == 'liner' or z_type == 'normal' or z_type == 'juggernaut':
        # Эти типы предполагают движение в указанном направлении на одну клетку
        move_map = {
            'left': (-1, 0), 'right': (1, 0), 'up': (0, -1), 'down': (0, 1)
        }
        dx, dy = move_map.get(direction, (0, 0))
        predicted_positions.append((x + dx, y + dy))

    elif z_type == 'bomber' or z_type == 'fast':
        # 'bomber' остаётся на месте, но его атака затрагивает соседние клетки
        # 'fast' перемещается на две клетки в указанном направлении
        if z_type == 'bomber':
            radius = 1
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if dx != 0 or dy != 0:  # Исключаем текущую позицию зомби
                        predicted_positions.append((x + dx, y + dy))
        elif z_type == 'fast':
            move_map = {
                'left': (-2, 0), 'right': (2, 0), 'up': (0, -2), 'down': (0, 2)
            }
            dx, dy = move_map.get(direction, (0, 0))
            predicted_positions.append((x + dx, y + dy))

    return predicted_positions


def prepare_attack_data(base_cells, zombies):
    """Подготавливает данные для команды атаки, учитывая текущие позиции зомби и ячейки базы."""
    attack_commands = []
    all_predicted_positions = []

    # Получаем предполагаемые позиции для всех зомби
    for zombie in zombies:
        predicted_positions = predict_fire_coordinates(zombie)
        all_predicted_positions.extend(predicted_positions)

    # Определяем, какие ячейки базы могут атаковать предполагаемые позиции зомби
    for cell in base_cells:
        for target in all_predicted_positions:
            if is_within_range(cell, target, cell['range']):
                attack_commands.append({
                    "blockId": cell['id'],
                    "target": {"x": target[0], "y": target[1]}
                })

    return {"attack": attack_commands}

def is_within_range(cell, target, range):
    """Проверяет, находится ли цель в радиусе действия ячейки."""
    return (cell['x'] - target[0]) ** 2 + (cell['y'] - target[1]) ** 2 <= range ** 2




units = get_units()
print(units)
zombies = units["zombies"]
base_cells = units["base"]

data = prepare_attack_data(base_cells, zombies)
while True:
    if zombies and base_cells:
        print(post_command(data))
    else:
        print("No zombies or base cells found")
    time.sleep(1)