# player.py
from .systems.skills import create_skills
from .systems.items import create_items
import time

class Player:
    def __init__(self, name="玩家"):
        self.name = name
        self.max_hp = 100
        self.hp = 100
        self.max_mp = 50
        self.mp = 50
        self.attack = 15
        self.defense = 5
        self.luck = 10
        
        # 临时属性
        self.temp_attack = 0  # 临时攻击力
        self.temp_defense = 0  # 临时防御力
        self.temp_effects = []  # 临时效果列表 [(效果类型, 值, 剩余回合)]
        
        self.skills = create_skills()
        self.items = create_items()
        self.inventory = []
        
        # 用于闪电链技能的敌人列表
        self.game_enemies = []

    def is_alive(self):
        return self.hp > 0

    def use_item(self, item):
        """使用道具"""
        try:
            # 应用道具效果
            item.effect(self)
            
            # 如果是临时效果，添加到临时效果列表
            if "temporary" in item.effect.__name__:
                duration = 3  # 默认持续3回合
                # 从道具配置中获取持续时间
                for item_config in self.items:
                    if item_config.name == item.name and hasattr(item_config, 'duration'):
                        duration = item_config.duration
                        break
                
                if "strength" in item.effect.__name__:
                    self.temp_effects.append(("attack", 10, duration))
                    self.temp_attack += 10
                elif "defense" in item.effect.__name__:
                    self.temp_effects.append(("defense", 5, duration))
                    self.temp_defense += 5
            
            # 从背包移除道具
            if item in self.inventory:
                self.inventory.remove(item)
            return True
        except Exception as e:
            print(f"使用道具出错: {e}")
            return False

    def get_effective_attack(self):
        """获取当前有效攻击力（包括临时加成）"""
        return self.attack + self.temp_attack

    def get_effective_defense(self):
        """获取当前有效防御力（包括临时加成）"""
        return self.defense + self.temp_defense

    def update_temp_effects(self):
        """更新临时效果，减少持续回合"""
        new_effects = []
        attack_change = 0
        defense_change = 0
        
        for effect_type, value, duration in self.temp_effects:
            if duration > 1:
                new_effects.append((effect_type, value, duration - 1))
            else:
                # 效果结束，需要减少属性
                if effect_type == "attack":
                    attack_change -= value
                elif effect_type == "defense":
                    defense_change -= value
        
        # 应用属性变化
        self.temp_attack += attack_change
        self.temp_defense += defense_change
        
        # 更新效果列表
        self.temp_effects = new_effects

    def clear_temp_effects(self):
        """清除所有临时效果"""
        self.temp_attack = 0
        self.temp_defense = 0
        self.temp_effects = []