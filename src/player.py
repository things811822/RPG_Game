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
        self.level = 1
        self.exp = 0
        self.gold = 0
        self.next_level_exp = 100
        # 临时属性
        self.temp_attack = 0  # 临时攻击力
        self.temp_defense = 0  # 临时防御力
        self.temp_effects = []  # 临时效果列表 [(效果类型, 值, 剩余回合)]
        self.skills = create_skills()
        self.items = create_items()
        self.inventory = []
        # 装备
        self.weapon = None
        self.armor = None
        self.accessory = None
        # 用于技能组合
        self.skill_history = []  # 存储最近使用的技能
        # 用于闪电链技能的敌人列表
        self.game_enemies = []
        # 复活石效果
        self.has_revive_stone = False
        self.revive_hp_percent = 0

    def is_alive(self):
        # 检查是否有复活石
        if self.hp <= 0 and self.has_revive_stone:
            self.hp = self.max_hp * (self.revive_hp_percent / 100)
            self.has_revive_stone = False
            return True
        return self.hp > 0 or getattr(self, 'god_mode', False)

    def use_item(self, item):
        """使用道具"""
        try:
            # 应用道具效果
            if hasattr(item, 'apply_effect'):
                # 新式道具系统
                return item.apply_effect(self)
            else:
                # 旧式道具系统
                if hasattr(item, 'effect_type'):
                    effect_type = item.effect_type
                else:
                    effect_type = item.effect.get('type', 'heal')
                
                if effect_type == 'heal':
                    heal_amount = item.effect.get('value', 30)
                    self.hp = min(self.max_hp, self.hp + heal_amount)
                    return f"💖 {self.name}使用了{item.name}，恢复 {heal_amount} HP！"
                elif effect_type == 'restore_mp':
                    mp_amount = item.effect.get('value', 20)
                    self.mp = min(self.max_mp, self.mp + mp_amount)
                    return f"💧 {self.name}使用了{item.name}，恢复 {mp_amount} MP！"
                elif effect_type == 'buff':
                    buff_type = item.effect.get('buff_type', 'attack')
                    buff_value = item.effect.get('value', 10)
                    duration = item.effect.get('duration', 3)
                    
                    if buff_type == 'attack':
                        self.temp_attack += buff_value
                        self.temp_effects.append(('attack', buff_value, duration))
                        return f"✨ {self.name}使用了{item.name}，攻击力提升 {buff_value}，持续 {duration} 回合！"
                    elif buff_type == 'defense':
                        self.temp_defense += buff_value
                        self.temp_effects.append(('defense', buff_value, duration))
                        return f"🛡️ {self.name}使用了{item.name}，防御力提升 {buff_value}，持续 {duration} 回合！"
                elif effect_type == 'permanent':
                    stat = item.effect.get('stat', 'max_hp')
                    value = item.effect.get('value', 5)
                    
                    if stat == 'max_hp':
                        self.max_hp += value
                        self.hp = min(self.max_hp, self.hp + value)
                        return f"⭐ {self.name}使用了{item.name}，最大HP永久提升 {value}！"
                    elif stat == 'attack':
                        self.attack += value
                        return f"⭐ {self.name}使用了{item.name}，攻击力永久提升 {value}！"
                    elif stat == 'defense':
                        self.defense += value
                        return f"⭐ {self.name}使用了{item.name}，防御力永久提升 {value}！"
                elif effect_type == 'special':
                    special_type = item.effect.get('special_type', 'revive')
                    value = item.effect.get('value', 50)
                    
                    if special_type == 'revive':
                        self.has_revive_stone = True
                        self.revive_hp_percent = value
                        return f"🔮 {self.name}获得了{item.name}，死亡时将自动复活并恢复 {value}% HP！"
            
            return f"✅ {self.name}使用了{item.name}！"
        except Exception as e:
            print(f"使用道具出错: {e}")
            return f"❌ 使用{item.name}时出错: {str(e)}"

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
                elif effect_type == "poison":
                    self.hp -= value
                    if self.hp <= 0 and not getattr(self, 'god_mode', False):
                        return False
        # 应用属性变化
        self.temp_attack += attack_change
        self.temp_defense += defense_change
        # 更新效果列表
        self.temp_effects = new_effects
        return True

    def clear_temp_effects(self):
        """清除所有临时效果"""
        self.temp_attack = 0
        self.temp_defense = 0
        self.temp_effects = []

    def add_experience(self, exp):
        """添加经验值"""
        self.exp += exp
        if self.exp >= self.next_level_exp:
            self.level_up()
    
    def level_up(self):
        """升级"""
        self.level += 1
        self.exp -= self.next_level_exp
        self.next_level_exp = int(self.next_level_exp * 1.5)
        
        # 升级奖励 - 按用户要求：每级提升3点攻击力，30点血量上限，并回满生命值
        self.max_hp += 30
        self.hp = self.max_hp
        self.attack += 3
        
        return f"🎉 {self.name}升级到{self.level}级！最大HP+30，攻击力+3！"