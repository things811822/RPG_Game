import os
import sys
import json
import random
from pathlib import Path
from .systems.utils import generate_perfect_maze, ensure_connectivity
from .systems.monsters import create_monster, get_monster_types, get_boss_config, get_config_path, get_boss_types
import math

WALL = 1
EMPTY = 0

class EnemySpot:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.enemy = create_monster(enemy_type)
        self.active = True
        # 检查是否为Boss
        self.is_boss = hasattr(self.enemy, 'is_boss') and self.enemy.is_boss

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
        self.is_boss_level = self.level % 10 == 0 and self.level > 0
        
        self.generate_content()

    def generate_content(self):
        """根据关卡类型生成内容"""
        if self.is_boss_level:
            self.generate_boss_level()
        else:
            self.generate_normal_level()

    def generate_boss_level(self):
        """生成Boss关卡内容（只生成Boss，不生成普通敌人）"""
        # 清空现有内容
        self.enemies = []
        self.items = []
        
        # 生成Boss
        self.generate_bosses()
        
        # 生成少量道具（Boss关卡）
        self.generate_items_for_boss_level()

    def generate_normal_level(self):
        """生成普通关卡内容（不生成Boss）"""
        # 清空现有内容
        self.enemies = []
        self.items = []
        
        # 生成普通敌人
        self.generate_normal_enemies()
        
        # 生成道具
        self.generate_items_for_normal_level()

    def generate_bosses(self):
        """生成随机Boss，数量和类型由配置决定"""
        # 获取所有符合条件的Boss
        available_bosses = self.get_available_bosses()
        
        # 如果没有可用Boss，返回
        if not available_bosses:
            print(f"警告：第{self.level}关没有可用的Boss配置")
            return
        
        # 随机选择一个Boss
        selected_boss = random.choice(available_bosses)
        
        # 在出口附近添加Boss
        boss_x, boss_y = self.find_boss_position()
        if boss_x is not None and boss_y is not None:
            self.enemies.append(EnemySpot(boss_x, boss_y, selected_boss['type']))
            self.boss_present = True
            print(f"Boss关卡{self.level}生成: {selected_boss['name']} at ({boss_x}, {boss_y})")
        else:
            print(f"警告：无法在第{self.level}关找到合适位置生成Boss")

    def get_available_bosses(self):
        """获取当前关卡可用的Boss列表"""
        available_bosses = []
        
        # 从配置文件获取所有Boss
        boss_types = get_boss_types()
        for boss_type in boss_types:
            boss_config = get_boss_config(boss_type)
            # 检查Boss是否应该在当前关卡或之前生成
            if boss_config and self.level >= boss_config.get('spawn_level', 10):
                available_bosses.append(boss_config)
        
        return available_bosses

    def find_boss_position(self):
        """寻找Boss的合适位置（在出口附近）"""
        # 在出口前2格处放置Boss
        boss_x = self.exit_point[0] - 2
        boss_y = self.exit_point[1] - 2
        if boss_x < 1: boss_x = 1
        if boss_y < 1: boss_y = 1
        
        # 确保Boss位置是空地
        if self.grid[boss_y][boss_x] == EMPTY:
            return boss_x, boss_y
        
        # 找最近的空地
        for distance in range(1, 6):  # 搜索5格范围
            for dx in range(-distance, distance + 1):
                for dy in range(-distance, distance + 1):
                    nx, ny = boss_x + dx, boss_y + dy
                    if 1 <= nx < self.size-1 and 1 <= ny < self.size-1:
                        if self.grid[ny][nx] == EMPTY:
                            return nx, ny
        
        return None, None

    def generate_normal_enemies(self):
        """生成普通敌人（不包括Boss）"""
        monster_types = get_monster_types()
        
        # 计算敌人数量（随关卡增加）
        num_enemies = min(3 + self.level//3, 8)
        
        for _ in range(num_enemies):
            while True:
                x = random.randint(1, self.size - 2)
                y = random.randint(1, self.size - 2)
                if self.grid[y][x] == EMPTY and (x, y) != (1, 1) and (x, y) != self.exit_point:
                    # 随机选择普通怪物类型
                    enemy_type = random.choice(monster_types)
                    self.enemies.append(EnemySpot(x, y, enemy_type))
                    break

    def generate_items_for_normal_level(self):
        """为普通关卡生成道具"""
        from .systems.items import create_items
        items = create_items()
        
        # 计算道具数量（随关卡增加）
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

    def generate_items_for_boss_level(self):
        """为Boss关卡生成少量道具"""
        from .systems.items import create_items
        items = create_items()
        
        # Boss关卡道具数量较少
        num_items = min(1 + self.level//10, 3)
        
        for _ in range(num_items):
            while True:
                x = random.randint(1, self.size - 2)
                y = random.randint(1, self.size - 2)
                if self.grid[y][x] == EMPTY and (x, y) != (1, 1) and (x, y) != self.exit_point:
                    # 随机选择道具
                    item = random.choice(items)
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
        """标记敌人被击败"""
        for e in self.enemies:
            if e.x == x and e.y == y and e.active:
                e.active = False
                # 检查是否是Boss
                if e.is_boss:
                    self.boss_present = False
                return True
        return False

    def collect_item(self, x, y):
        for i in self.items:
            if i.x == x and i.y == y and i.active:
                i.active = False
                return i.item
        return None

    def add_boss_at_exit(self):
        """在出口附近添加Boss，用于作弊功能"""
        # 获取所有可用Boss
        available_bosses = self.get_available_bosses()
        if not available_bosses:
            print("警告：没有可用的Boss类型")
            return False
        
        # 随机选择一个Boss
        selected_boss = random.choice(available_bosses)
        
        # 检查是否已经有Boss
        boss_count = sum(1 for enemy in self.enemies if enemy.is_boss)
        if boss_count >= selected_boss.get('max_occurrences', 1):
            print(f"无法在出口添加Boss: 已达到最大数量 {selected_boss.get('max_occurrences', 1)}")
            return False
        
        # 在出口前2格处放置Boss
        boss_x = self.exit_point[0] - 2
        boss_y = self.exit_point[1] - 2
        if boss_x < 1: boss_x = 1
        if boss_y < 1: boss_y = 1
        
        # 确保Boss位置是空地
        if self.grid[boss_y][boss_x] == EMPTY:
            # 检查该位置是否已经有敌人
            has_enemy = any(enemy.x == boss_x and enemy.y == boss_y for enemy in self.enemies)
            if not has_enemy:
                self.enemies.append(EnemySpot(boss_x, boss_y, selected_boss['type']))
                print(f"成功在出口 ({boss_x}, {boss_y}) 添加Boss: {selected_boss['name']}")
                self.boss_present = True
                return True
        
        # 找最近的空地
        for distance in range(1, 6):  # 搜索5格范围
            for dx in range(-distance, distance + 1):
                for dy in range(-distance, distance + 1):
                    nx, ny = boss_x + dx, boss_y + dy
                    if 1 <= nx < self.size-1 and 1 <= ny < self.size-1:
                        if self.grid[ny][nx] == EMPTY:
                            # 检查该位置是否已经有敌人
                            has_enemy = any(enemy.x == nx and enemy.y == ny for enemy in self.enemies)
                            if not has_enemy:
                                self.enemies.append(EnemySpot(nx, ny, selected_boss['type']))
                                print(f"成功在出口附近 ({nx}, {ny}) 添加Boss: {selected_boss['name']}")
                                self.boss_present = True
                                return True
        
        print("无法在出口附近添加Boss: 无法找到合适的空地")
        return False