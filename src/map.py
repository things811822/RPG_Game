from .systems.utils import generate_perfect_maze
import random

WALL = 1
EMPTY = 0

class EnemySpot:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.active = True

class ItemSpot:
    def __init__(self, x, y, item):
        self.x = x
        self.y = y
        self.item = item
        self.active = True

class GameMap:
    def __init__(self, size=11):
        self.size = size
        # 确保大小为奇数
        if size % 2 == 0:
            size += 1
            self.size = size
            
        self.grid = generate_perfect_maze(size)
        self.player_x = 1.0
        self.player_y = 1.0
        self.enemies = []
        self.items = []
        self.exit_point = (size-2, size-2)
        self.generate_content()

    def generate_content(self):
        enemy_types = ["goblin", "skeleton", "spider", "orc"]
        # 放置敌人
        for _ in range(random.randint(3, 5)):
            while True:
                x = random.randint(1, self.size - 2)
                y = random.randint(1, self.size - 2)
                if self.grid[y][x] == EMPTY and (x, y) != (1, 1) and (x, y) != self.exit_point:
                    self.enemies.append(EnemySpot(x, y, random.choice(enemy_types)))
                    break

        # 放置道具
        from .systems.items import Item
        healing_potion = Item("治疗药水", "恢复 30 HP", lambda p: setattr(p, 'hp', min(p.max_hp, p.hp + 30)))
        mp_potion = Item("魔法药水", "恢复 20 MP", lambda p: setattr(p, 'mp', min(p.max_mp, p.mp + 20)))
        items_pool = [healing_potion, mp_potion]
        for _ in range(random.randint(2, 3)):
            while True:
                x = random.randint(1, self.size - 2)
                y = random.randint(1, self.size - 2)
                if self.grid[y][x] == EMPTY and (x, y) != (1, 1) and (x, y) != self.exit_point:
                    item = random.choice(items_pool)
                    self.items.append(ItemSpot(x, y, item))
                    break

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