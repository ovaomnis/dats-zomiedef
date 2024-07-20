import time

from requ import get_units, post_command, get_world


def is_valid_build_position(x, y, base_cells, zombies, enemyBlocks, zpots):
    """Проверяет, можно ли строить на данной позиции, учитывая существующие ограничения."""
    # Проверяем, занята ли уже эта позиция клеткой базы
    if any(cell['x'] == x and cell['y'] == y for cell in base_cells):
        return False
    if zombies:
        # Проверяем, есть ли зомби на этой позиции или рядом с ней
        if any(zombie['x'] == x and zombie['y'] == y for zombie in zombies):
            return False
        if any(zombie['x'] == x + dx and zombie['y'] == y + dy for zombie in zombies for dx in [-1, 0, 1] for dy in [-1, 0, 1]):
            return False

    # Проверяем, находится ли позиция слишком близко к вражеским блокам или точкам респавна
    min_distance_to_enemy = 1  # Минимальное расстояние до вражеских блоков
    min_distance_to_zpot = 1   # Минимальное расстояние до точек респавна зомби
    if enemyBlocks:
        if any(abs(enemyBlock['x'] - x) <= min_distance_to_enemy and abs(enemyBlock['y'] - y) <= min_distance_to_enemy for enemyBlock in enemyBlocks):
            return False
    if any(abs(zpot['x'] - x) <= min_distance_to_zpot and abs(zpot['y'] - y) <= min_distance_to_zpot for zpot in zpots):
        return False

    return True



def prepare_build_data(base_cells, zombies, gold, enemyBlocks, zpots):
    """Оптимизированное строительство с учетом оборонной стратегии, сетки с пропусками и доступного золота."""
    builds = []
    head_cell = next((cell for cell in base_cells if cell.get('isHead', False)), None)
    if not head_cell:
        print("Главная ячейка не найдена.")
        return builds

    all_cells = set((cell['x'], cell['y']) for cell in base_cells)
    directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]  # Стратегическое движение через одну клетку

    # Перебираем каждую ячейку и проверяем возможные позиции для строительства
    for cell in base_cells:
        for dx, dy in directions:
            new_x, new_y = cell['x'] + dx, cell['y'] + dy
            if (new_x, new_y) not in all_cells and is_valid_build_position(new_x, new_y, base_cells, zombies, enemyBlocks, zpots):
                adjacent_x1, adjacent_y1 = cell['x'] + dx // 2, cell['y'] + dy // 2
                adjacent_x2, adjacent_y2 = cell['x'] - dx // 2, cell['y'] - dy // 2
                if ((adjacent_x1, adjacent_y1) in all_cells or (adjacent_x2, adjacent_y2) in all_cells):
                    if gold > 0:  # Проверяем, есть ли достаточно золота для строительства
                        builds.append({'x': new_x, 'y': new_y})
                        all_cells.add((new_x, new_y))
                        gold -= 1  # Уменьшаем количество доступного золота
                    else:
                        break

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

def predict_fire_coordinates(zombie):
    """Вычисляет текущие координаты зомби для непосредственной атаки."""
    x, y = zombie['x'], zombie['y']
    return [(x, y)]  # Возвращаем список с одной парой координат


def prepare_attack_data(base_cells, zombies, enemyBlocks, gold, zpots):
    """Подготавливает данные для команды атаки, учитывая текущие позиции зомби и ячейки базы."""
    attack_commands = []
    all_current_positions = [predict_fire_coordinates(zombie) for zombie in zombies]

    # Словарь для контроля количества атак каждой ячейкой
    cell_targets = {}

    # Определяем, какие ячейки базы могут атаковать текущие позиции зомби
    if base_cells:
        for cell in base_cells:
            for target in all_current_positions:
                if is_within_range(cell, target[0], cell['range']):
                    if cell['id'] not in cell_targets:
                        cell_targets[cell['id']] = target[0]
                        break

    # Формирование команд атаки на основе назначенных целей
    for cell_id, target in cell_targets.items():
        attack_commands.append({
            "blockId": cell_id,
            "target": {"x": target[0], "y": target[1]}
        })

    builds = prepare_build_data(base_cells, zombies, gold, enemyBlocks, zpots)

    return {"attack": attack_commands, "build": builds}


    builds = prepare_build_data(base_cells, zombies, gold, enemyBlocks, zpots)

    return {"attack": attack_commands, "build": builds}



def is_within_range(cell, target, range):
    """Проверяет, находится ли цель в радиусе действия ячейки."""
    return (cell['x'] - target[0]) ** 2 + (cell['y'] - target[1]) ** 2 <= range ** 2




while True:
    units = get_units()
    if 'error' in units:
        print("Error fetching units:", units)
        time.sleep(1)
        continue

    try:
        print(units["player"]["zombieKills"], units["player"]["enemyBlockKills"], units["player"]["gold"], len(units["base"]))
    except Exception as e:
        print("Error while printing units", e)
        time.sleep(10)
        continue
    zombies = units["zombies"]
    base_cells = units["base"]
    enemyBlocks = units["enemyBlocks"]
    zpots = get_world()["zpots"]
    try:
        data = prepare_attack_data(base_cells, zombies, enemyBlocks, units["player"]["gold"], zpots)
        #data["moveBase"] =  {"x": 472, "y": 8} # moveBase)
    except Exception as e:
        print("Error while preparing attack data", e)
        continue
    if not data:
        continue
    if zombies and base_cells:
       response = post_command(data)

    else:
        print("No zombies or base cells found")

    turn_ends_in_ms = units.get('turnEndsInMs', 2000)
    time.sleep(turn_ends_in_ms / 1000)