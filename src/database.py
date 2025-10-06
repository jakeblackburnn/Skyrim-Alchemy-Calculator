import csv
from .effect import Effect
from .ingredient import Ingredient

class IngredientsDatabase:

    def __init__(self):
        self.ingredients_file = open("data/master_ingredients.csv", newline = '')
        self.ingredients_reader = csv.reader(self.ingredients_file)

    def get_ingredient(self, name):
        self.ingredients_file.seek(0)
        next(self.ingredients_reader)

        for row in self.ingredients_reader:
            ingredient_name = row[0]
            if ingredient_name == name:
                line = ','.join(row)
                return Ingredient.from_csv_line(line)

        return None

    def print_self(self):
        for row in self.ingredients_reader:
            print(row)

    def __del__(self):
        self.ingredients_file.close()

class EffectsDatabase: 

    def __init__(self):
        self.effects_file = open("data/effects.csv", newline = '')
        self.effects_reader = csv.reader(self.effects_file)

    def default_effect(self, name):
        self.effects_file.seek(0)
        next(self.effects_reader)

        for row in self.effects_reader:
            effect_name = row[0]
            if effect_name == name:
                line = ','.join(row)
                return Effect.from_csv_line(line)

        return None

    def ingredient_effect(self, effect_name, ingredient):
        default_effect = self.default_effect(effect_name)
        if default_effect is None:
            return None

        effect_data = ingredient.get_effect_data(effect_name)
        if effect_data is None:
            return None

        mag, dur = effect_data
        default_effect.base_mag = mag
        default_effect.base_dur = dur

        return default_effect

    def print_self(self):
        for row in self.effects_reader:
            print(row)

    def __del__(self):
        self.effects_file.close()

if __name__ == "__main__":

    ing_dat = IngredientsDatabase()
    eff_dat = EffectsDatabase()

    ing_dat.print_self()
    eff_dat.print_self()

    del ing_dat
    del eff_dat

    print("databases successfully deleted.")

