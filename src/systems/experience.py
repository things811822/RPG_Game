import json
import os
from pathlib import Path
import sys

def get_experience_config():
    """获取经验配置"""
    config_path = get_config_path('experience.json')
    
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('experience', {})
        except Exception as e:
            print(f"加载经验配置文件出错: {e}")
    
    # 默认经验配置
    return {
        "goblin": 10,
        "spider": 8,
        "skeleton": 15,
        "zombie": 20,
        "bat": 5,
        "slime": 3,
        "wolf": 12,
        "giant_spider": 18,
        "dragon": 100,
        "giant_dragon": 200,
        "demon_king": 300
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