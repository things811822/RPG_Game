import json
import os
import sys
from pathlib import Path
from ..battle import Enemy
from .experience import get_experience_config

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
    config_path = get_config_path('boss_config.json')
    
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return [boss['type'] for boss in config['bosses']]
        except Exception as e:
            print(f"加载Boss配置文件出错: {e}")
    
    # 默认Boss类型
    return ["dragon"]

def get_monster_config(monster_type):
    """获取特定怪物的配置，优先从配置文件加载"""
    config_path = get_config_path('monsters.json')
    
    # 仅当配置文件存在时尝试加载
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # 在配置文件中查找匹配的怪物
            for monster in config['monsters']:
                if monster['type'] == monster_type:
                    return monster
            # 配置文件存在但没有找到匹配的怪物
            print(f"警告：配置文件中没有找到怪物类型 '{monster_type}'")
        except Exception as e:
            print(f"加载怪物配置文件出错: {e}")
    
    # 作为备选，使用内建的默认配置
    return get_default_monster_config(monster_type)

def get_default_monster_config(monster_type):
    """获取内置默认怪物配置"""
    default_configs = {
        "goblin": {
            "type": "goblin",
            "name": "哥布林",
            "max_hp": 20,
            "attack": 5,
            "defense": 10,
            "color": "#aa5555"
        },
        "spider": {
            "type": "spider",
            "name": "蜘蛛",
            "max_hp": 15,
            "attack": 3,
            "defense": 8,
            "color": "#55aa55"
        },
        "skeleton": {
            "type": "skeleton",
            "name": "骷髅",
            "max_hp": 25,
            "attack": 6,
            "defense": 12,
            "color": "#aaaaaa"
        },
        "zombie": {
            "type": "zombie",
            "name": "僵尸",
            "max_hp": 30,
            "attack": 4,
            "defense": 15,
            "color": "#55aa55"
        },
        "bat": {
            "type": "bat",
            "name": "蝙蝠",
            "max_hp": 10,
            "attack": 2,
            "defense": 5,
            "color": "#5555aa"
        },
        "slime": {
            "type": "slime",
            "name": "史莱姆",
            "max_hp": 12,
            "attack": 1,
            "defense": 3,
            "color": "#55ff55"
        },
        "wolf": {
            "type": "wolf",
            "name": "狼",
            "max_hp": 18,
            "attack": 5,
            "defense": 10,
            "color": "#aaa555"
        },
        "giant_spider": {
            "type": "giant_spider",
            "name": "巨蜘蛛",
            "max_hp": 25,
            "attack": 4,
            "defense": 15,
            "color": "#aa55aa"
        },
        "dragon": {
            "type": "dragon",
            "name": "火龙",
            "max_hp": 100,
            "attack": 15,
            "defense": 25,
            "color": "#ff5555"
        },
        "giant_dragon": {
            "type": "giant_dragon",
            "name": "巨龙",
            "max_hp": 150,
            "attack": 20,
            "defense": 30,
            "color": "#ff8855"
        },
        "demon_king": {
            "type": "demon_king",
            "name": "恶魔之王",
            "max_hp": 200,
            "attack": 25,
            "defense": 40,
            "color": "#5555ff"
        }
    }
    
    # 返回匹配的配置，如果没有匹配则返回通用默认配置
    if monster_type in default_configs:
        return default_configs[monster_type]
    
    # 通用默认配置
    return {
        "type": monster_type,
        "name": "未知怪物",
        "max_hp": 20,
        "attack": 5,
        "defense": 10,
        "color": "#aaaaaa"
    }

def get_boss_config(boss_type):
    """获取特定Boss的配置"""
    config_path = get_config_path('boss_config.json')
    
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            for boss in config['bosses']:
                if boss['type'] == boss_type:
                    return boss
        except Exception as e:
            print(f"加载Boss配置文件出错: {e}")
    
    # 默认Boss配置
    return get_default_boss_config(boss_type)

def get_default_boss_config(boss_type):
    """获取内置默认Boss配置"""
    default_configs = {
        "dragon": {
            "type": "dragon",
            "name": "火龙",
            "description": "古老的火龙，守护着关卡的出口",
            "max_occurrences": 1,
            "spawn_level": 10,
            "is_boss_level": True
        },
        "giant_dragon": {
            "type": "giant_dragon",
            "name": "巨龙",
            "description": "更强大的龙类Boss",
            "max_occurrences": 1,
            "spawn_level": 20,
            "is_boss_level": True
        },
        "demon_king": {
            "type": "demon_king",
            "name": "恶魔之王",
            "description": "地狱的统治者，拥有毁灭性力量",
            "max_occurrences": 1,
            "spawn_level": 30,
            "is_boss_level": True
        }
    }
    
    if boss_type in default_configs:
        return default_configs[boss_type]
    
    # 通用默认Boss配置
    return {
        "type": boss_type,
        "name": "Boss",
        "max_occurrences": 1,
        "spawn_level": 10,
        "is_boss_level": False
    }

def get_config_path(filename):
    """获取配置文件路径"""
    # 尝试从exe同级目录的config文件夹获取
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的exe
        base_path = Path(sys.executable).parent
    else:
        # 开发环境
        base_path = Path(__file__).parent.parent.parent
    
    # 检查主配置目录
    config_path = base_path / "config" / filename
    if config_path.exists():
        return str(config_path)
    
    # 检查其他可能的路径
    possible_paths = [
        Path(__file__).parent.parent.parent.parent / "config" / filename,
        Path(__file__).parent / "config" / filename,
        Path(getattr(sys, '_MEIPASS', '')) / "config" / filename
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    # 所有路径都不存在
    return None

def create_monster(monster_type):
    """创建怪物实例，优先使用配置文件"""
    # 获取怪物配置
    monster_config = get_monster_config(monster_type)
    
    # 获取经验值
    exp_config = get_experience_config()
    exp_value = exp_config.get(monster_type, 10)
    
    # 获取金币值（如果有配置）
    gold_value = monster_config.get('gold', 5)
    
    # 创建怪物
    enemy = Enemy(
        monster_config['name'],
        monster_config['max_hp'],
        monster_config['attack'],
        monster_config['defense'],
        gold_value
    )
    
    # 添加经验值
    enemy.exp = exp_value
    
    # 设置颜色
    enemy.color = monster_config.get('color', "#aaaaaa")
    
    # 检查是否为Boss
    boss_config = get_boss_config(monster_type)
    if boss_config.get('is_boss_level', False):
        enemy.is_boss = True
    
    return enemy