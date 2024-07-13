import time

from requ import get_world, get_units, post_command

def is_valid_build_position(x, y, base_cells, zombies):

    """Проверяет, можно ли строить на данной позиции."""
    if any((cell['x'] == x and cell['y'] == y) for cell in base_cells):
        return False  # Нельзя строить на занятой ячейке базы
    if zombies:
        if any((zombie['x'] == x and zombie['y'] == y) for zombie in zombies):
            return False  # Нельзя строить на ячейке с зомби

    # Проверка соседних клеток
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if any((zombie['x'] == x + dx and zombie['y'] == y + dy) for zombie in zombies):
                return False  # Нельзя строить рядом с зомби

    return True


def prepare_build_data(base_cells, zombies):
    """Оптимизированное строительство с учетом оборонной стратегии и пропусков."""
    builds = []
    head_cell = next((cell for cell in base_cells if cell.get('isHead', False)), None)
    if not head_cell:
        print("Главная ячейка не найдена.")
        return builds

    all_cells = set((cell['x'], cell['y']) for cell in base_cells)
    strategic_positions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
    secondary_positions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for cell in base_cells:
        # Приоритет строительства в стратегических позициях
        for dx, dy in strategic_positions:
            new_x, new_y = cell['x'] + dx, cell['y'] + dy
            if (new_x, new_y) not in all_cells and is_valid_build_position(new_x, new_y, base_cells, zombies):
                builds.append({'x': new_x, 'y': new_y})
                all_cells.add((new_x, new_y))
        # Вторичное строительство в менее важных позициях
        for dx, dy in secondary_positions:
            new_x, new_y = cell['x'] + dx, cell['y'] + dy
            if (new_x, new_y) not in all_cells and is_valid_build_position(new_x, new_y, base_cells, zombies):
                builds.append({'x': new_x, 'y': new_y})
                all_cells.add((new_x, new_y))

    print(f"Планируется строительство {len(builds)} новых ячеек.")
    return builds




def predict_fire_coordinates(zombie):
    """Вычисляет координаты для атаки на упреждение, учитывая тип, скорость и задержку зомби."""
    x, y, z_type, direction = zombie['x'], zombie['y'], zombie['type'], zombie.get('direction', '')
    speed = zombie.get('speed', 1)  # Значение по умолчанию, если скорость не указана
    wait_turns = zombie.get('waitTurns', 0)  # Значение по умолчанию, если задержка не указана
    predicted_positions = []

    if wait_turns > 0:
        # Зомби ожидает, не двигаясь
        predicted_positions.append((x, y))
    else:
        if z_type in ['liner', 'normal', 'juggernaut', 'bomber']:
            move_map = {
                'left': (-1, 0), 'right': (1, 0), 'up': (0, -1), 'down': (0, 1)
            }
            dx, dy = move_map.get(direction, (0, 0))
            for step in range(1, speed + 1):  # Учитываем скорость зомби
                predicted_positions.append((x + dx * step, y + dy * step))

        elif z_type == 'fast':
            move_map = {
                'left': (-1, 0), 'right': (1, 0), 'up': (0, -1), 'down': (0, 1)
            }
            dx, dy = move_map.get(direction, (0, 0))
            predicted_positions.append((x + dx * speed, y + dy * speed))

        elif z_type == 'chaos_knight':
            knight_moves = {
                'left': [(-1, 2), (-1, -2)],
                'right': [(1, 2), (1, -2)],
                'up': [(2, -1), (-2, -1)],
                'down': [(2, 1), (-2, 1)]
            }
            possible_moves = knight_moves.get(direction, [])
            for move in possible_moves:
                predicted_positions.append((x + move[0], y + move[1]))

    return predicted_positions



def prepare_attack_data(base_cells, zombies, enemyBlocks):
    """Подготавливает данные для команды атаки, учитывая текущие позиции зомби и ячейки базы."""
    attack_commands = []
    all_predicted_positions = []

    # Сортировка зомби по здоровью, затем получение предполагаемых позиций
    if zombies:
        sorted_zombies = sorted(zombies, key=lambda z: z.get('health', float('inf')))  # Сортируем по здоровью, меньшее здоровье имеет приоритет
        for zombie in sorted_zombies:
            predicted_positions = predict_fire_coordinates(zombie)
            all_predicted_positions.extend(predicted_positions)

    if enemyBlocks:
        for enemyBlock in enemyBlocks:
            all_predicted_positions.append((enemyBlock['x'], enemyBlock['y']))

    # Определяем, какие ячейки базы могут атаковать предполагаемые позиции
    if base_cells:
        for cell in base_cells:
            for target in all_predicted_positions:
                if is_within_range(cell, target, cell['range']):
                    attack_commands.append({
                        "blockId": cell['id'],
                        "target": {"x": target[0], "y": target[1]}
                    })
        builds = prepare_build_data(base_cells, zombies)

    return {"attack": attack_commands, "build": builds}


def is_within_range(cell, target, range):
    """Проверяет, находится ли цель в радиусе действия ячейки."""
    return (cell['x'] - target[0]) ** 2 + (cell['y'] - target[1]) ** 2 <= range ** 2




while True:
    units = get_units()
    if 'error' in units:
        print("Error fetching units:", units)
        time.sleep(0.5)
        continue


    print(units["player"]["zombieKills"], units["player"]["enemyBlockKills"], units["player"]["gold"], len(units["base"]))
    zombies = units["zombies"]
    base_cells = units["base"]
    enemyBlocks = units["enemyBlocks"]
    try:
        data = prepare_attack_data(base_cells, zombies, enemyBlocks)
       # data["moveBase"] =  {"x": 173, "y": 169} # moveBase)
    except Exception as e:
        print("Error while preparing attack data", e)
        continue
    if not data:
        continue
    if zombies and base_cells:
       post_command(data)
    else:
        print("No zombies or base cells found")

    turn_ends_in_ms = units.get('turnEndsInMs', 2000)
    time.sleep(turn_ends_in_ms / 1000)