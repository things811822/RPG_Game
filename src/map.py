from .systems.utils import generate_perfect_maze, ensure_connectivity
from .systems.monsters import create_monster, get_monster_types
import random

WALL = 1
EMPTY = 0

class EnemySpot:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.enemy = create_monster(enemy_type)
        self.active = True

class ItemSpot:
    def __init__(self, x, y, item):
        self.x = x
        self.y = y
        self.item = item
        self.active = True

class GameMap:
    def __init__(self, size=11, level=1):
        self.size = size
        # 确保大小为奇数
        if size % 2 == 0:
            size += 1
            self.size = size
            
        # 生成并确保连通性
        self.grid = generate_perfect_maze(size)
        self.grid = ensure_connectivity(self.grid)
        
        self.player_x = 1.0
        self.player_y = 1.0
        self.enemies = []
        self.items = []
        self.exit_point = (size-2, size-2)
        self.level = level
        self.boss_present = False
        
        self.generate_content()

    def generate_content(self):
        monster_types = get_monster_types()
        
        # 每5关添加boss
        if self.level % 5 == 0:
            self.add_boss()
        
        # 放置敌人
        num_enemies = min(3 + self.level//3, 8)
        for _ in range(num_enemies):
            while True:
                x = random.randint(1, self.size - 2)
                y = random.randint(1, self.size - 2)
                if self.grid[y][x] == EMPTY and (x, y) != (1, 1) and (x, y) != self.exit_point:
                    # 随机选择怪物类型
                    enemy_type = random.choice(monster_types)
                    self.enemies.append(EnemySpot(x, y, enemy_type))
                    break

        # 放置道具
        from .systems.items import create_items
        items = create_items()
        num_items = min(2 + self.level//4, 5)
        for _ in range(num_items):
            while True:
                x = random.randint(1, self.size - 2)
                y = random.randint(1, self.size - 2)
                if self.grid[y][x] == EMPTY and (x, y) != (1, 1) and (x, y) != self.exit_point:
                    # 随机选择道具
                    item = random.choice(items)
                    self.items.append(ItemSpot(x, y, item))
                    break

    def add_boss(self):
        """在出口前添加boss"""
        self.boss_present = True
        # 在出口前2格处放置boss
        boss_x = self.exit_point[0] - 2
        boss_y = self.exit_point[1] - 2
        if boss_x < 1: boss_x = 1
        if boss_y < 1: boss_y = 1
        
        # 确保boss位置是空地
        if self.grid[boss_y][boss_x] == EMPTY:
            self.enemies.append(EnemySpot(boss_x, boss_y, "dragon"))
        else:
            # 找最近的空地
            for i in range(1, 5):
                for dx in range(-i, i+1):
                    for dy in range(-i, i+1):
                        nx, ny = boss_x + dx, boss_y + dy
                        if 1 <= nx < self.size-1 and 1 <= ny < self.size-1 and self.grid[ny][nx] == EMPTY:
                            self.enemies.append(EnemySpot(nx, ny, "dragon"))
                            return

    def is_wall(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[y][x] == WALL
        return True

    def move_player(self, dx, dy):
        nx, ny = self.player_x + dx, self.player_y + dy
        if not self.is_wall(int(nx), int(ny)):
            self.player_x, self.player_y = nx, ny
            return True
        return False

    def get_enemy_at(self, x, y):
        for e in self.enemies:
            if e.x == x and e.y == y and e.active:
                return e
        return None

    def get_item_at(self, x, y):
        for i in self.items:
            if i.x == x and i.y == y and i.active:
                return i
        return None

    def defeat_enemy(self, x, y):
        for e in self.enemies:
            if e.x == x and e.y == y:
                e.active = False
                return True
        return False

    def collect_item(self, x, y):
        for i in self.items:
            if i.x == x and i.y == y and i.active:
                i.active = False
                return i.item
        return None