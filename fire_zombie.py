import time

from requ import get_world, get_units, post_command

def is_valid_build_position(x, y, base_cells, zombies):
    """Проверяет, можно ли строить на данной позиции."""
    if any((cell['x'] == x and cell['y'] == y) for cell in base_cells):
        return False  # Нельзя строить на занятой ячейке базы

    if any((zombie['x'] == x and zombie['y'] == y) for zombie in zombies):
        return False  # Нельзя строить на ячейке с зомби

    # Проверка соседних клеток
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if any((zombie['x'] == x + dx and zombie['y'] == y + dy) for zombie in zombies):
                return False  # Нельзя строить рядом с зомби

    return True


def prepare_build_data(base_cells, zombies):
    """Подготавливает данные для строительства новых ячеек, фокусируясь вокруг главной ячейки."""
    builds = []
    try:
        head_cell = next((cell for cell in base_cells if cell['isHead']), None)
    except Exception:
        head_cell = None

    if not head_cell:
        return builds  # Если главная ячейка не найдена, возвращаем пустой список

    # Создаём список клеток для построения с приоритетом вокруг главной ячейки
    directions = [(dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if not (dx == 0 and dy == 0)]
    potential_builds = [(head_cell['x'] + dx, head_cell['y'] + dy) for dx, dy in directions]

    # Добавляем остальные ячейки базы
    for cell in base_cells:
        if cell != head_cell:
            additional_builds = [(cell['x'] + dx, cell['y'] + dy) for dx, dy in directions]
            potential_builds.extend(additional_builds)

    # Проверяем каждую потенциальную позицию на возможность строительства
    for new_x, new_y in potential_builds:
        if is_valid_build_position(new_x, new_y, base_cells, zombies):
            builds.append({'x': new_x, 'y': new_y})

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
    if not base_cells:
        return
    """Подготавливает данные для команды атаки, учитывая текущие позиции зомби и ячейки базы."""
    attack_commands = []
    all_predicted_positions = []

    # Получаем предполагаемые позиции для всех зомби
    for zombie in zombies:
        predicted_positions = predict_fire_coordinates(zombie)
        all_predicted_positions.extend(predicted_positions)

    # Получаем позиции вражеских блоков и ищем главную ячейку противника
    enemy_positions = [(block['x'], block['y']) for block in enemyBlocks]
    head_enemy_block = next((block for block in enemyBlocks if block.get('isHead', False)), None)

    # Определяем, какие ячейки базы могут атаковать все цели, включая зомби и блоки
    for cell in base_cells:
        if head_enemy_block and is_within_range(cell, (head_enemy_block['x'], head_enemy_block['y']), cell['range']):
            # Если главная ячейка врага в диапазоне, добавляем только её
            attack_commands.append({
                "blockId": cell['id'],
                "target": {"x": head_enemy_block['x'], "y": head_enemy_block['y']}
            })
        else:
            # Иначе проверяем все цели
            for target in all_predicted_positions + enemy_positions:
                if is_within_range(cell, target, cell['range']):
                    attack_commands.append({
                        "blockId": cell['id'],
                        "target": {"x": target[0], "y": target[1]}
                    })
                    break  # Предотвращаем повторную атаку на те же координаты

    builds = prepare_build_data(base_cells, zombies)

    return {"attack": attack_commands, "build": builds}


def is_within_range(cell, target, range):
    """Проверяет, находится ли цель в радиусе действия ячейки."""
    return (cell['x'] - target[0]) ** 2 + (cell['y'] - target[1]) ** 2 <= range ** 2





while True:
    units = get_units()
    try:
        if units["error"]:
            print(units)
            time.sleep(0.5)
            continue
    except KeyError:
        pass


    print(units["player"]["zombieKills"], units["player"]["enemyBlockKills"], units["player"]["gold"])
    zombies = units["zombies"]
    base_cells = units["base"]
    enemyBlocks = units["enemyBlocks"]

    data = prepare_attack_data(base_cells, zombies, enemyBlocks)
    if not data:
        continue
    if zombies and base_cells:
       post_command(data)
    else:
        print("No zombies or base cells found")

    time.sleep(2)
