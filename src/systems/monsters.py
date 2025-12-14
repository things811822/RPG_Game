from .utils import load_config
from ..battle import Enemy  # 修复：使用正确的相对导入路径

def create_monster(monster_type):
    """从配置文件创建怪物"""
    config = load_config('monsters.json')
    
    for monster_config in config.get('monsters', []):
        if monster_config['type'] == monster_type:
            return Enemy(
                name=monster_config['name'],
                max_hp=monster_config['max_hp'],
                attack=monster_config['attack'],
                defense=monster_config['defense'],
                is_boss=monster_config.get('is_boss', False)
            )
    
    # 默认创建哥布林
    return Enemy("哥布林", 30, 8, 2)

def get_monster_types():
    """获取所有怪物类型"""
    config = load_config('monsters.json')
    return [m['type'] for m in config.get('monsters', [])]