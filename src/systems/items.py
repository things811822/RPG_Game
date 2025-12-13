class Item:
    def __init__(self, name, desc, effect):
        self.name = name
        self.desc = desc
        self.effect = effect

    def __str__(self):
        return f"{self.name}: {self.desc}"