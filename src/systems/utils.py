WALL = 1
EMPTY = 0

import random
import json
import os
import sys
from pathlib import Path

def load_config(filename):
    """
    加载配置文件
    
    优先级顺序：
    1. exe 同级目录下的 config/ 文件夹（支持热更新）
    2. 开发环境的项目根目录 config/ 
    3. 回退到相对路径（兼容旧逻辑）
    """
    # === 方法 1: 优先读取 exe 旁边的 config（支持热更新）===
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的 exe
        external_config_path = Path(sys.executable).parent / "config" / filename
    else:
        # 开发环境
        external_config_path = Path(__file__).parent.parent.parent / "config" / filename
    
    if external_config_path.exists():
        try:
            with open(external_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"警告: 无法读取外部配置文件 {external_config_path}: {e}")

    # === 方法 2: 回退到原始相对路径逻辑（兼容性）===
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', filename)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置文件 {filename} 失败: {e}")
        return {}

def generate_perfect_maze(size):
    """
    生成基于房间的迷宫（100%连通，有房间感）
    使用递归分割算法
    """
    # 确保大小为奇数
    if size % 2 == 0:
        size += 1
    
    # 创建全墙网格
    grid = [[WALL for _ in range(size)] for _ in range(size)]
    
    # 确保边界是墙壁
    for i in range(size):
        grid[0][i] = WALL
        grid[size-1][i] = WALL
        grid[i][0] = WALL
        grid[i][size-1] = WALL
    
    # 递归分割
    def divide(x, y, width, height):
        if width < 5 or height < 5:
            # 创建房间
            for i in range(x+1, x+width-1):
                for j in range(y+1, y+height-1):
                    grid[j][i] = EMPTY
            return
        
        # 选择分割线
        divide_x = x + random.randint(2, width-3)
        divide_y = y + random.randint(2, height-3)
        
        # 水平分割
        if random.random() < 0.5:
            # 创建水平墙
            for i in range(x+1, x+width-1):
                grid[divide_y][i] = WALL
            
            # 创建通道
            passage_x = x + random.randint(1, width-2)
            grid[divide_y][passage_x] = EMPTY
            
            # 递归
            divide(x, y, width, divide_y-y+1)
            divide(x, divide_y, width, height-(divide_y-y))
        else:
            # 创建垂直墙
            for j in range(y+1, y+height-1):
                grid[j][divide_x] = WALL
            
            # 创建通道
            passage_y = y + random.randint(1, height-2)
            grid[passage_y][divide_x] = EMPTY
            
            # 递归
            divide(x, y, divide_x-x+1, height)
            divide(divide_x, y, width-(divide_x-x), height)
    
    # 初始分割
    divide(0, 0, size, size)
    
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