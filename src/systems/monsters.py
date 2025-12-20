import json
import os
import sys
from pathlib import Path
from ..battle import Enemy

def get_monster_types():
    """获取所有普通怪物类型（不包括Boss）"""
    monster_types = [
        "goblin", 
        "spider", 
        "skeleton", 
        "zombie",
        "bat",
        "slime",
        "wolf",
        "giant_spider"
    ]
    return monster_types

def get_boss_types():
    """获取所有Boss类型"""
    # 从配置文件加载Boss类型
    config_path = get_config_path('boss_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return [boss['type'] for boss in config['bosses']]
    except Exception as e:
        print(f"加载Boss配置文件出错: {e}")
        # 默认Boss类型
        return ["dragon"]

def get_boss_config(boss_type):
    """获取特定Boss的配置"""
    config_path = get_config_path('boss_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        for boss in config['bosses']:
            if boss['type'] == boss_type:
                return boss
    except Exception as e:
        print(f"加载Boss配置文件出错: {e}")
        pass
    
    # 默认配置
    return {
        "type": boss_type,
        "name": "Boss",
        "max_occurrences": 1,
        "spawn_level": 10
    }

def get_config_path(filename):
    """获取配置文件路径"""
    # 调试：打印当前文件路径
    print(f"当前文件路径: {Path(__file__)}")
    
    # 尝试从exe同级目录的config文件夹获取
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的exe
        base_path = Path(sys.executable).parent
    else:
        # 开发环境
        base_path = Path(__file__).parent.parent.parent
    
    config_path = base_path / "config" / filename
    
    # 调试：打印配置文件路径
    print(f"配置文件路径: {config_path}")
    
    # 如果配置文件存在，返回路径
    if config_path.exists():
        print(f"找到配置文件: {config_path}")
        return str(config_path)
    
    # 尝试其他可能的路径
    possible_paths = [
        # 项目根目录的config
        Path(__file__).parent.parent.parent.parent / "config" / filename,
        # 当前目录的config
        Path(__file__).parent / "config" / filename,
        # 打包后的_temp目录
        Path(getattr(sys, '_MEIPASS', '')) / "config" / filename
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"在备用路径找到配置文件: {path}")
            return str(path)
    
    # 所有路径都不存在，打印错误
    print(f"警告: 无法找到配置文件 {filename}，所有尝试路径:")
    for path in [config_path] + possible_paths:
        print(f"  - {path} {'存在' if path.exists() else '不存在'}")
    
    return None

def create_monster(monster_type):
    """创建怪物实例"""
    # Boss配置
    boss_config = get_boss_config(monster_type)
    
    if monster_type == "goblin":
        return Enemy("哥布林", 20, 5, 10, 10)
    elif monster_type == "spider":
        return Enemy("蜘蛛", 15, 3, 8, 15)
    elif monster_type == "skeleton":
        return Enemy("骷髅", 25, 6, 12, 10)
    elif monster_type == "zombie":
        return Enemy("僵尸", 30, 4, 15, 20)
    elif monster_type == "bat":
        return Enemy("蝙蝠", 10, 2, 5, 25)
    elif monster_type == "slime":
        return Enemy("史莱姆", 12, 1, 3, 30)
    elif monster_type == "wolf":
        return Enemy("狼", 18, 5, 10, 20)
    elif monster_type == "giant_spider":
        return Enemy("巨蜘蛛", 25, 4, 15, 25)
    elif monster_type == "dragon":
        enemy = Enemy("火龙", 100, 15, 25, 5)
        enemy.is_boss = True
        return enemy
    elif monster_type == "giant_dragon":
        enemy = Enemy("巨龙", 150, 20, 30, 3)
        enemy.is_boss = True
        return enemy
    elif monster_type == "demon_king":
        enemy = Enemy("恶魔之王", 200, 25, 40, 2)
        enemy.is_boss = True
        return enemy
    else:
        # 默认怪物
        return Enemy("未知怪物", 20, 5, 10, 10)