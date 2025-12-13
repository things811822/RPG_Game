# utils.py
WALL = 1
EMPTY = 0

import random

def generate_perfect_maze(size):
    """
    生成完美迷宫（无环、连通）
    使用递归分割算法
    """
    # 确保大小为奇数
    if size % 2 == 0:
        size += 1
    
    # 创建全墙网格
    grid = [[WALL for _ in range(size)] for _ in range(size)]
    
    # 创建内部通道
    for i in range(1, size-1):
        for j in range(1, size-1):
            grid[i][j] = EMPTY
    
    # 递归分割
    def divide(x, y, width, height, orientation):
        if width < 3 or height < 3:
            return
        
        # 创建墙
        if orientation == 0:  # 水平分割
            # 选择分割行（奇数）
            divide_y = y + random.randint(1, height//2) * 2
            # 创建墙
            for i in range(x, x + width):
                grid[divide_y][i] = WALL
            
            # 创建通道
            passage_x = x + random.randint(0, width//2) * 2
            grid[divide_y][passage_x] = EMPTY
            
            # 递归
            divide(x, y, width, divide_y - y, 1)
            divide(x, divide_y + 1, width, y + height - divide_y - 1, 1)
        else:  # 垂直分割
            # 选择分割列（奇数）
            divide_x = x + random.randint(1, width//2) * 2
            # 创建墙
            for i in range(y, y + height):
                grid[i][divide_x] = WALL
            
            # 创建通道
            passage_y = y + random.randint(0, height//2) * 2
            grid[passage_y][divide_x] = EMPTY
            
            # 递归
            divide(x, y, divide_x - x, height, 0)
            divide(divide_x + 1, y, x + width - divide_x - 1, height, 0)
    
    # 初始分割
    divide(1, 1, size-2, size-2, random.randint(0, 1))
    
    # 确保入口和出口
    grid[1][1] = EMPTY  # 入口
    grid[size-2][size-2] = EMPTY  # 出口
    
    return grid