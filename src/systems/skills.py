class Skill:
    def __init__(self, name, mp_cost, description, effect_func):
        self.name = name
        self.mp_cost = mp_cost
        self.description = description
        self.effect_func = effect_func

    def can_use(self, player):
        return player.mp >= self.mp_cost

    def use(self, player, target=None):
        if self.can_use(player):
            player.mp -= self.mp_cost
            return self.effect_func(player, target)
        return "魔法值不足！"