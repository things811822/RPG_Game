# items.py
from .utils import load_config

class Item:
    def __init__(self, name, description, effect_config):
        self.name = name
        self.description = description
        self.effect_config = effect_config
        self.effect_type = effect_config.get('type', 'heal')

    def apply_effect(self, player):
        """应用物品效果"""
        # 根据效果类型应用不同效果
        if self.effect_type == 'heal':
            return self._apply_heal(player)
        elif self.effect_type == 'restore_mp':
            return self._apply_restore_mp(player)
        elif self.effect_type == 'buff':
            return self._apply_buff(player)
        elif self.effect_type == 'debuff':
            return self._apply_debuff(player)
        elif self.effect_type == 'special':
            return self._apply_special(player)
        else:
            return f"使用了 {self.name}！"

    def _apply_heal(self, player):
        """应用治疗效果"""
        heal_amount = self.effect_config.get('value', 30)
        player.hp = min(player.max_hp, player.hp + heal_amount)
        return f"💖 {self.name}恢复 {heal_amount} HP！"

    def _apply_restore_mp(self, player):
        """应用魔法恢复效果"""
        mp_amount = self.effect_config.get('value', 20)
        player.mp = min(player.max_mp, player.mp + mp_amount)
        return f"💧 {self.name}恢复 {mp_amount} MP！"

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

    def _apply_debuff(self, player):
        """应用减益效果（对玩家）"""
        debuff_type = self.effect_config.get('debuff_type', 'attack')
        debuff_value = self.effect_config.get('value', 10)
        duration = self.effect_config.get('duration', 3)
        
        # 添加临时效果
        if debuff_type == 'attack':
            player.temp_attack -= debuff_value
            player.temp_effects.append(('debuff_attack', debuff_value, duration))
        elif debuff_type == 'defense':
            player.temp_defense -= debuff_value
            player.temp_effects.append(('debuff_defense', debuff_value, duration))
        
        return f"⚠️ {self.name}降低 {debuff_value} {debuff_type}，持续 {duration} 回合！"

    def _apply_special(self, player):
        """应用特殊效果"""
        special_type = self.effect_config.get('special_type', 'teleport')
        value = self.effect_config.get('value', 1)
        
        if special_type == 'teleport':
            return f"💫 {self.name}将你传送到随机位置！"
        elif special_type == 'experience':
            return f"🌟 {self.name}获得 {value} 经验值！"
        else:
            return f"✨ {self.name}触发特殊效果！"

def create_items():
    """从配置文件创建道具"""
    config = load_config('items.json')
    items = []
    
    for item_config in config.get('items', []):
        name = item_config['name']
        description = item_config['description']
        effect_config = item_config['effect']
        
        items.append(Item(name, description, effect_config))
    
    return items