from itertools import combinations
from .potion import Potion
from .player import Player
from .inventory import Inventory
from .ingredient import Ingredient
from .database import IngredientsDatabase

class Alembic:

    def __init__(self, db=IngredientsDatabase(), player=Player(), inventory=None):
        self._ing_db = db 
        self.player = player
        self.inventory = inventory  

        # Only generate potions if ingredients provided
        if inventory is not None:
            self._set_all_valid_potions()
        else:
            self.potions = []  # Initialize empty list

    def _set_all_valid_potions(self):
        ingredients_list = self.inventory.get_available_ingredients()
        valid_combos = []

        for combo in combinations(ingredients_list, 2):
            if self._has_shared_effects(combo):
                valid_combos.append(list(combo))

        for combo in combinations(ingredients_list, 3):
            if self._has_shared_effects(combo):
                valid_combos.append(list(combo))

        self.potions = [Potion(combo, self.player, self._ing_db) for combo in valid_combos]

    def _has_shared_effects(self, ingredients):
        # Get effect sets for each ingredient
        ingredient_effects = [set(ing.get_effect_names()) for ing in ingredients]

        # For each ingredient, check if it shares at least one effect with another
        for i, effects_i in enumerate(ingredient_effects):
            has_shared = False
            for j, effects_j in enumerate(ingredient_effects):
                if i != j and len(effects_i & effects_j) > 0:
                    has_shared = True
                    break
            if not has_shared:
                return False

        return True

    def get_value_sorted_potions(self):
        return sorted(self.potions, key=lambda p: p.total_value, reverse=True)

    def filter_by_ingredient(self, ingredient=None):
        return filter(lambda p: any([i is ingredient for i in p.ingredients()]), self.potions)


    # sets the player object and regenerates potions if inventory exists
    def update_player(self, new_player):
        self.player = new_player
        if self.inventory is not None:
            self._set_all_valid_potions()

    def set_inventory(self, inventory):
        if not isinstance(inventory, Inventory):
            raise TypeError(f"Expected Inventory instance, got {type(inventory)}")

        self.inventory = inventory
        self._set_all_valid_potions()

    def exhaust_inventory(self, strategy="greedy-basic"):
        if self.inventory is None:
            raise ValueError("No inventory set. Call set_inventory() first.")

        if strategy == "greedy-basic":
            return self._greedy_basic_strategy()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def _greedy_basic_strategy(self):
        potions_made = []

        while not self.inventory.is_empty():
            # Update ingredients from current inventory state
            self.ingredients_list = self.inventory.get_available_ingredients()

            # No more valid potions possible
            if not self.potions:
                break

            # Select highest-value potion
            best = max(self.potions, key=lambda p: p.total_value)

            # Consume ingredients
            if self.inventory.consume_recipe(best.ingredients):
                potions_made.append(best)
                self._set_all_valid_potions()
            else:
                break  # Safety check

        return potions_made

    def delete_inventory(self):
        self.inventory = None
        self.potions = []

def main():

    db = IngredientsDatabase()
    print("generating inventory...")
    inv = Inventory.generate_normal(db, 7)

    player = Player()

    alembic = Alembic(db, player, inv)
    print("printing inventory\n=================\n")
    print(inv)

    print("\ncreating potions...")
    potions = alembic.exhaust_inventory()

    print("printing potions\n================\n")
    for potion in potions:
        print(potion)

    print("printing inventory\n=================\n")
    print(inv)




if __name__ == "__main__":
    main()
