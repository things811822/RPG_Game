from .systems.skills import Skill
from .systems.items import Item

class Player:
    def __init__(self):
        self.max_hp = 100
        self.hp = 100
        self.max_mp = 50
        self.mp = 50
        self.attack = 15
        self.defense = 5
        self.luck = 10

        self.skills = [
            Skill("火球术", 10, "造成 25 点魔法伤害",
                  lambda p, e: (e.take_damage(25) or f"🔥 火球术造成 25 伤害！") if e else ""),
            Skill("治疗术", 15, "恢复 40 HP",
                  lambda p, e: (setattr(p, 'hp', min(p.max_hp, p.hp + 40)) or "💖 治疗术恢复 40 HP！"))
        ]

        self.inventory = []

    def is_alive(self):
        return self.hp > 0

    def use_item(self, item):
        if item.effect:
            item.effect(self)
            self.inventory.remove(item)
            return True
        return False