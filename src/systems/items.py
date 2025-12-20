import json
import os
from pathlib import Path
import sys

class Item:
    def __init__(self, name, description, effect_config, boss_reward=False):
        self.name = name
        self.description = description
        self.effect_config = effect_config
        self.effect_type = effect_config.get('type', 'heal')
        self.boss_reward = boss_reward
    
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
        elif self.effect_type == 'permanent':
            return self._apply_permanent(player)
        elif self.effect_type == 'special':
            return self._apply_special(player)
        else:
            return f"使用了 {self.name}！"
    
    def _apply_heal(self, player):
        """应用治疗效果"""
        heal_amount = self.effect_config.get('value', 30)
        player.hp = min(player.max_hp, player.hp + heal_amount)
        return f"💖 {player.name}使用了{self.name}，恢复 {heal_amount} HP！"
    
    def _apply_restore_mp(self, player):
        """应用魔法恢复效果"""
        mp_amount = self.effect_config.get('value', 20)
        player.mp = min(player.max_mp, player.mp + mp_amount)
        return f"💧 {player.name}使用了{self.name}，恢复 {mp_amount} MP！"
    
    def _apply_buff(self, player):
        """应用增益效果"""
        buff_type = self.effect_config.get('buff_type', 'attack')
        buff_value = self.effect_config.get('value', 10)
        duration = self.effect_config.get('duration', 3)
        
        # 添加临时效果
        if buff_type == 'attack':
            player.temp_attack += buff_value
            player.temp_effects.append(('attack', buff_value, duration))
            return f"✨ {player.name}使用了{self.name}，攻击力提升 {buff_value}，持续 {duration} 回合！"
        elif buff_type == 'defense':
            player.temp_defense += buff_value
            player.temp_effects.append(('defense', buff_value, duration))
            return f"🛡️ {player.name}使用了{self.name}，防御力提升 {buff_value}，持续 {duration} 回合！"
    
    def _apply_debuff(self, target):
        """应用减益效果（对目标）"""
        debuff_type = self.effect_config.get('debuff_type', 'attack')
        debuff_value = self.effect_config.get('value', 10)
        duration = self.effect_config.get('duration', 3)
        
        # 对目标应用减益
        if hasattr(target, 'debuffs'):
            target.debuffs.append((debuff_type, debuff_value, duration))
            return f"⚠️ {self.name}降低目标 {debuff_value} {debuff_type}，持续 {duration} 回合！"
        return "无法应用减益效果：目标无效"
    
    def _apply_permanent(self, player):
        """应用永久效果"""
        stat = self.effect_config.get('stat', 'max_hp')
        value = self.effect_config.get('value', 5)
        
        if stat == 'max_hp':
            player.max_hp += value
            player.hp = min(player.max_hp, player.hp + value)
            return f"⭐ {player.name}使用了{self.name}，最大HP永久提升 {value}！"
        elif stat == 'attack':
            player.attack += value
            return f"⭐ {player.name}使用了{self.name}，攻击力永久提升 {value}！"
        elif stat == 'defense':
            player.defense += value
            return f"⭐ {player.name}使用了{self.name}，防御力永久提升 {value}！"
    
    def _apply_special(self, player):
        """应用特殊效果"""
        special_type = self.effect_config.get('special_type', 'revive')
        value = self.effect_config.get('value', 50)
        
        if special_type == 'revive':
            player.has_revive_stone = True
            player.revive_hp_percent = value
            return f"🔮 {player.name}获得了{self.name}，死亡时将自动复活并恢复 {value}% HP！"
        else:
            return f"✨ {player.name}触发了{self.name}的特殊效果！"

def get_config_path(filename):
    """获取配置文件路径"""
    # 尝试从exe同级目录的config文件夹获取
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的exe
        base_path = Path(sys.executable).parent
    else:
        # 开发环境
        base_path = Path(__file__).parent.parent.parent
    
    config_path = base_path / "config" / filename
    
    # 如果配置文件不存在，尝试从源代码目录获取
    if not config_path.exists():
        possible_paths = [
            Path(__file__).parent.parent.parent.parent / "config" / filename,
            Path(__file__).parent / "config" / filename,
            Path(getattr(sys, '_MEIPASS', '')) / "config" / filename
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
    
    return str(config_path)

def create_items():
    """从配置文件创建道具"""
    config_path = get_config_path('items.json')
    items = []
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        for item_config in config.get('items', []):
            name = item_config['name']
            description = item_config['description']
            effect_config = item_config['effect']
            boss_reward = item_config.get('boss_reward', False)
            
            items.append(Item(name, description, effect_config, boss_reward))
    
    except Exception as e:
        print(f"加载道具配置文件出错: {e}")
        # 创建默认道具
        items = [
            Item("小型治疗药水", "恢复20点HP", {'type': 'heal', 'value': 20}),
            Item("魔法药水", "恢复15点MP", {'type': 'restore_mp', 'value': 15}),
            Item("力量药水", "临时提升10点攻击力，持续3回合", 
                {'type': 'buff', 'buff_type': 'attack', 'value': 10, 'duration': 3}),
            Item("防御药水", "临时提升5点防御力，持续3回合", 
                {'type': 'buff', 'buff_type': 'defense', 'value': 5, 'duration': 3}),
            Item("经验药水", "永久提升5点最大HP", 
                {'type': 'permanent', 'stat': 'max_hp', 'value': 5}, boss_reward=True),
            Item("神圣武器", "临时提升15点攻击力，持续5回合", 
                {'type': 'buff', 'buff_type': 'attack', 'value': 15, 'duration': 5}, boss_reward=True),
            Item("龙鳞护盾", "临时提升10点防御力，持续5回合", 
                {'type': 'buff', 'buff_type': 'defense', 'value': 10, 'duration': 5}, boss_reward=True),
            Item("复活石", "死亡时自动复活并恢复50%HP", 
                {'type': 'special', 'special_type': 'revive', 'value': 50}, boss_reward=True, consumable_on_death=True)
        ]
    
    return items