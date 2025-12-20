# skills.py
import random
from .utils import load_config

class Skill:
    def __init__(self, name, mp_cost, description, effect_config):
        self.name = name
        self.mp_cost = mp_cost
        self.description = description
        self.effect_config = effect_config
        self.effect_type = effect_config.get('type', 'damage')

    def can_use(self, player):
        return player.mp >= self.mp_cost

    def use(self, player, target=None):
        if self.can_use(player):
            player.mp -= self.mp_cost
            
            # 根据效果类型应用不同效果
            if self.effect_type == 'damage':
                return self._apply_damage(player, target)
            elif self.effect_type == 'heal':
                return self._apply_heal(player)
            elif self.effect_type == 'buff':
                return self._apply_buff(player)
            elif self.effect_type == 'debuff':
                return self._apply_debuff(player, target)
            elif self.effect_type == 'multi_target':
                return self._apply_multi_target(player, target)
            else:
                return f"使用了 {self.name}！"
        return "魔法值不足！"

    def _apply_damage(self, player, target):
        """应用伤害效果"""
        damage = self.effect_config.get('value', 25)
        if target:
            target.take_damage(damage)
            return f"🔥 {player.name}释放{self.name}，造成 {damage} 伤害！"
        return "无法应用伤害效果：目标不存在"

    def _apply_heal(self, player):
        """应用治疗效果"""
        heal_amount = self.effect_config.get('value', 40)
        player.hp = min(player.max_hp, player.hp + heal_amount)
        return f"💖 {self.name}恢复 {heal_amount} HP！"

    def _apply_buff(self, player):
        """应用增益效果"""
        buff_type = self.effect_config.get('buff_type', 'attack')
        buff_value = self.effect_config.get('value', 10)
        duration = self.effect_config.get('duration', 3)
        
        # 添加临时效果
        if buff_type == 'attack':
            player.temp_attack += buff_value
            player.temp_effects.append(('attack', buff_value, duration))
        elif buff_type == 'defense':
            player.temp_defense += buff_value
            player.temp_effects.append(('defense', buff_value, duration))
        
        return f"✨ {self.name}提升 {buff_value} {buff_type}，持续 {duration} 回合！"

    def _apply_debuff(self, player, target):
        """应用减益效果"""
        debuff_type = self.effect_config.get('debuff_type', 'attack')
        debuff_value = self.effect_config.get('value', 10)
        duration = self.effect_config.get('duration', 3)
        
        # 对目标应用减益
        if target and hasattr(target, 'debuffs'):
            target.debuffs.append((debuff_type, debuff_value, duration))
            return f"⚠️ {self.name}降低目标 {debuff_value} {debuff_type}，持续 {duration} 回合！"
        return "无法应用减益效果：目标无效"

    def _apply_multi_target(self, player, target):
        """应用多目标效果（如闪电链）"""
        damage = self.effect_config.get('value', 30)
        damage_log = []
        
        # 假设player有game_enemies属性
        if hasattr(player, 'game_enemies'):
            for enemy_spot in player.game_enemies:
                if enemy_spot.active and enemy_spot.enemy.is_alive():
                    enemy_spot.enemy.take_damage(damage)
                    damage_log.append(f"{enemy_spot.enemy.name} -{damage}")
        
        if damage_log:
            return f"⚡ {self.name}击中 {len(damage_log)} 个敌人: " + ", ".join(damage_log)
        return "⚡ 闪电链没有击中任何敌人"

def create_skills():
    """从配置文件创建技能"""
    config = load_config('skills.json')
    skills = []
    
    for skill_config in config.get('skills', []):
        name = skill_config['name']
        mp_cost = skill_config['mp_cost']
        description = skill_config['description']
        effect_config = skill_config['effect']
        
        skills.append(Skill(name, mp_cost, description, effect_config))
    
    return skills

def check_skill_combo(player):
    """检查技能组合效果"""
    last_two_skills = player.skill_history[-2:] if len(player.skill_history) >= 2 else []
    
    if len(last_two_skills) == 2:
        skill1, skill2 = last_two_skills
        
        # 火球术 + 闪电链 = 超级闪电
        if "火球术" in skill1.name and "闪电链" in skill2.name:
            return {
                "name": "🔥⚡ 超级闪电",
                "description": "火与电的完美结合！对所有敌人造成50点伤害！",
                "effect": lambda p, t: (
                    f"💥 超级闪电对所有敌人造成 50 伤害！" if 
                    [e.take_damage(50) for e in getattr(p, 'game_enemies', []) if e.is_alive()] else 
                    "💥 超级闪电没有击中任何敌人！"
                )
            }
        
        # 治疗术 + 力量祝福 = 圣光护盾
        elif "治疗术" in skill1.name and "力量祝福" in skill2.name:
            return {
                "name": "✨🛡️ 圣光护盾",
                "description": "治疗与强化的结合，赋予护盾！提升15防御，持续3回合！",
                "effect": lambda p, t: (
                    setattr(p, 'temp_defense', p.temp_defense + 15) or 
                    p.temp_effects.append(('defense', 15, 3)) or
                    "💫 圣光护盾提升 15 防御力，持续 3 回合！"
                )
            }
        
        # 虚弱术 + 闪电链 = 麻痹连锁
        elif "虚弱术" in skill1.name and "闪电链" in skill2.name:
            return {
                "name": "⚡⛓️ 麻痹连锁",
                "description": "削弱敌人防御后释放闪电链，伤害提升25%！",
                "effect": lambda p, t: (
                    [e.take_damage(38) for e in getattr(p, 'game_enemies', []) if e.is_alive()] and 
                    "⚡ 麻痹连锁对所有敌人造成 38 伤害！"
                )
            }
    
    return None