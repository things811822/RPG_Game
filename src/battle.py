# battle.py
class Enemy:
    def __init__(self, name, max_hp, attack, defense, is_boss=False):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense
        self.is_boss = is_boss

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        self.hp -= dmg