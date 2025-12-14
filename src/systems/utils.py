# src/systems/utils.py
WALL = 1
EMPTY = 0

import random
import json
import os
import sys
from pathlib import Path

def load_config(filename):
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).resolve().parent.parent.parent

    external_config_path = app_dir / "config" / filename
    if external_config_path.exists():
        try:
            with open(external_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"警告: 无法读取外部配置文件 {external_config_path}: {e}")

    try:
        if getattr(sys, 'frozen', False):
            internal_path = Path(getattr(sys, '_MEIPASS')) / "config" / filename
        else:
            internal_path = app_dir / "config" / filename

        with open(internal_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"错误: 无法加载配置文件 {filename}: {e}")
        return {}

def generate_perfect_maze(size):
    # 确保大小为奇数
    if size % 2 == 0:
        size += 1
    
    # 创建全墙网格
    grid = [[WALL for _ in range(size)] for _ in range(size)]
    
    # 创建内部通道
    for i in range(1, size-1):
        for j in range(1, size-1):
            grid[i][j] = EMPTY
    
    # 确保边界是墙壁
    for i in range(size):
        grid[0][i] = WALL
        grid[size-1][i] = WALL
        grid[i][0] = WALL
        grid[i][size-1] = WALL
    
    # 使用迭代DFS生成迷宫
    visited = [[False for _ in range(size)] for _ in range(size)]
    stack = [(1, 1)]
    visited[1][1] = True
    
    while stack:
        x, y = stack.pop()
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < size-1 and 1 <= ny < size-1 and not visited[ny][nx] and grid[ny][nx] == EMPTY:
                # 打通墙壁
                grid[y + dy//2][x + dx//2] = EMPTY
                visited[ny][nx] = True
                stack.append((nx, ny))
    
    # 确保入口和出口
    grid[1][1] = EMPTY  # 入口
    grid[size-2][size-2] = EMPTY  # 出口
    
    return grid

def is_path_available(grid, start, end):
    """检查两点之间是否有路径（BFS算法）"""
    size = len(grid)
    visited = [[False for _ in range(size)] for _ in range(size)]
    queue = []
    
    # 初始化队列
    queue.append(start)
    visited[start[1]][start[0]] = True
    
    # BFS
    while queue:
        x, y = queue.pop(0)
        
        # 到达终点
        if (x, y) == end:
            return True
        
        # 检查四个方向
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size:
                if not visited[ny][nx] and grid[ny][nx] == EMPTY:
                    visited[ny][nx] = True
                    queue.append((nx, ny))
    
    return False

def ensure_connectivity(grid):
    """确保所有点都连通"""
    size = len(grid)
    for i in range(1, size-1):
        for j in range(1, size-1):
            if grid[j][i] == EMPTY:
                if not is_path_available(grid, (1, 1), (i, j)):
                    # 连接不通的区域
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < size and 0 <= nj < size and grid[nj][ni] == WALL:
                            grid[nj][ni] = EMPTY
                            break
    return grid