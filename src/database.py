import csv
import warnings
from .effect import Effect
from .ingredient import Ingredient
from .inventory import Inventory

class IngredientsDatabase:

    def __init__(self, data_dir="data"):
        self._ingredients = {}  # Dict[str, Ingredient]
        self._load_ingredients(data_dir)

    def _load_ingredients(self, data_dir):
        """Load all ingredients from CSV into dictionary (called once)."""
        with open(f"{data_dir}/master_ingredients.csv", newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header

            for row in reader:
                line = ','.join(row)
                ingredient = Ingredient.from_csv_line(line)
                self._ingredients[ingredient.name] = ingredient

    def get_ingredient(self, name):
        """O(1) lookup by name from in-memory dictionary."""
        return self._ingredients.get(name)

    def get_all_ingredients(self):
        """Return list of all ingredients from in-memory dictionary.

        Returns:
            List of all Ingredient objects from the database
        """
        return list(self._ingredients.values())

    def sample_inventory(self, strategy: str, size: int = None):
        """DEPRECATED: Use Inventory.generate_*() methods instead.

        This method will be removed in version 2.0.

        Migration guide:
            Old: db.sample_inventory("vendor")
            New: Inventory.generate_vendor(db).get_available_ingredients()

        Args:
            strategy: Sampling strategy ('normal', 'random_weighted', or 'vendor')
            size: Number of ingredients (ignored for 'vendor' strategy)

        Returns:
            List of ingredient names
        """
        warnings.warn(
            "sample_inventory() is deprecated and will be removed in version 2.0. "
            "Use Inventory.generate_normal(), Inventory.generate_random_weighted(), "
            "or Inventory.generate_vendor() instead.",
            DeprecationWarning,
            stacklevel=2
        )

        # Delegate to new Inventory class
        if strategy == "normal":
            inv = Inventory.generate_normal(self, size)
        elif strategy == "random_weighted":
            inv = Inventory.generate_random_weighted(self, size)
        elif strategy == "vendor":
            inv = Inventory.generate_vendor(self)
        else:
            raise ValueError(
                f"Invalid strategy '{strategy}'. "
                f"Must be one of: ['normal', 'random_weighted', 'vendor']"
            )

        return inv.get_available_ingredients()

    def print_self(self):
        """Debug helper to print all ingredients."""
        for name, ingredient in self._ingredients.items():
            print(f"{name}: {ingredient}")

    def __repr__(self):
        return f"IngredientsDatabase({len(self._ingredients)} ingredients loaded)"

    def __len__(self):
        """Returns total number of ingredients in database."""
        return len(self._ingredients)

    def __contains__(self, name: str) -> bool:
        """Support: if 'ingredient' in db"""
        return name in self._ingredients

    def __getitem__(self, name: str):
        """Support: ingredient = db['name']
        Raises KeyError if ingredient not found (alternative to get_ingredient() which returns None)."""
        if name not in self._ingredients:
            raise KeyError(f"Ingredient '{name}' not found in database")
        return self._ingredients[name]

    def __iter__(self):
        """Support: for ingredient in db
        Yields Ingredient objects (not names)."""
        return iter(self._ingredients.values())





class EffectsDatabase: 

    def __init__(self, data_dir="data"):
        self.effects_file = open(f"{data_dir}/effects.csv", newline = '')
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

