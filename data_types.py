from dataclasses import dataclass

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class LastAttack:
    x: int
    y: int

@dataclass
class Base:
    attack: int
    health: int
    id: str
    isHead: bool
    lastAttack: LastAttack
    range: int
    x: int
    y: int

@dataclass
class EnemyBlock:
    attack: int
    health: int
    isHead: bool
    lastAttack: LastAttack
    name: str
    x: int
    y: int

@dataclass
class Player:
    enemyBlockKills: int
    gameEndedAt: datetime
    gold: int
    name: str
    points: int
    zombieKills: int

@dataclass
class Zombie:
    attack: int
    direction: str
    health: int
    id: str
    speed: int
    type: str
    waitTurns: int
    x: int
    y: int

@dataclass
class fetchUnitsResponse:
    base: List[Base]
    enemyBlocks: List[EnemyBlock]
    player: Player
    realmName: str
    turn: int
    turnEndsInMs: int
    zombies: List[Zombie]
