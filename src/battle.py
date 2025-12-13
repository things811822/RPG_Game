class Enemy:
    def __init__(self, name, max_hp, attack, defense):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        self.hp -= dmg