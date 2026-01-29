from itertools import combinations
from .potion import Potion
from .player import Player
from .inventory import Inventory
from .database import IngredientsDatabase, EffectsDatabase

class Alembic:

    def __init__(self, player_stats, ingredients_list=None):
        self.ingredients_list = ingredients_list
        self.player = Player.from_dict(player_stats)
        self.ingredients_db = IngredientsDatabase()
        self.effects_db = EffectsDatabase()
        self._inventory = None  # Add inventory state tracking

        # Only generate potions if ingredients provided
        if ingredients_list is not None:
            self.generate_potions()
        else:
            self.potions = []  # Initialize empty list

    @classmethod
    def from_base_player(cls, ingredients_list=None):
        """Create an AlchemySimulator with a default Player (skill=15, no perks).

        Args:
            ingredients_list: Optional list of ingredient names. If None,
                            creates simulator without generating potions.
        """
        base_player_stats = {
            "alchemy_skill": 15,
            "fortify_alchemy": 0,
            "alchemist_perk": 0,
            "physician_perk": False,
            "benefactor_perk": False,
            "poisoner_perk": False,
            "seeker_of_shadows": False,
            "purity_perk": False
        }
        return cls(base_player_stats, ingredients_list)

    def generate_potions(self):
        valid_combinations = []

        for combo in combinations(self.ingredients_list, 2):
            if self._has_shared_effects(combo):
                valid_combinations.append(list(combo))

        for combo in combinations(self.ingredients_list, 3):
            if self._has_shared_effects(combo):
                valid_combinations.append(list(combo))

        self.potions = [Potion(combination, self.player, self.ingredients_db, self.effects_db) for combination in valid_combinations]

    def _has_shared_effects(self, ingredient_names):
        # Get all ingredients
        ingredients = [self.ingredients_db.get_ingredient(name) for name in ingredient_names]

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

    def print_potions(self):
        print(f"Total Potions: {len(self.potions)}\n")
        sorted_potions = sorted(self.potions, key=lambda p: p.total_value, reverse=True)
        for i, potion in enumerate(sorted_potions, 1):
            print(f"--- Potion {i} ---")
            potion.print_self()
            print()


    def update_player(self, player_stats):
        self.player = Player.from_dict(player_stats)
        # Only regenerate if we have ingredients
        if self.ingredients_list is not None:
            self.generate_potions()

    def add_ingredient(self, ingredient_name):
        # check that ingredient doesnt already exist
        if self.ingredients_list is None:
            self.ingredients_list = []

        if ingredient_name not in self.ingredients_list:
            self.ingredients_list.append(ingredient_name)
            self.generate_potions()

    def remove_ingredient(self, ingredient_name):
        # check that ingredient is in ingredients list
        if self.ingredients_list is not None and ingredient_name in self.ingredients_list:
            self.ingredients_list.remove(ingredient_name)
            self.generate_potions()

    def set_inventory(self, inventory):
        """Set current inventory and regenerate potions.

        Args:
            inventory: Inventory instance with ingredient quantities

        Raises:
            TypeError: If inventory is not an Inventory instance
        """

        if not isinstance(inventory, Inventory):
            raise TypeError(f"Expected Inventory instance, got {type(inventory)}")

        self._inventory = inventory
        self.ingredients_list = inventory.get_available_ingredients()
        self.generate_potions()

    def exhaust_inventory(self, strategy="greedy-basic"):
        """Run potion-making strategy that consumes current inventory.

        Args:
            strategy: Algorithm to use ("greedy-basic" supported)

        Returns:
            List of Potion objects created in order

        Raises:
            ValueError: If no inventory set or unknown strategy
        """
        if self._inventory is None:
            raise ValueError("No inventory set. Call set_inventory() first.")

        if strategy == "greedy-basic":
            return self._greedy_basic_strategy()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def _greedy_basic_strategy(self):
        """Greedy algorithm: repeatedly make highest-value potion.

        Returns:
            List of Potion objects created
        """
        potions_made = []

        while not self._inventory.is_empty():
            # Update ingredients from current inventory state
            self.ingredients_list = self._inventory.get_available_ingredients()
            self.generate_potions()

            # No more valid potions possible
            if not self.potions:
                break

            # Select highest-value potion
            best = max(self.potions, key=lambda p: p.total_value)

            # Consume ingredients
            if self._inventory.consume_recipe(best.ingredient_names):
                potions_made.append(best)
            else:
                break  # Safety check

        return potions_made

    def delete_inventory(self):
        """Clear current inventory and reset potion state.

        Preserves player stats for reuse with new inventory.
        """
        self._inventory = None
        self.ingredients_list = None
        self.potions = []

    @staticmethod
    def greedy_potionmaking(player_stats, inventory):
        """Run greedy algorithm consuming inventory.

        Creates potions by repeatedly selecting the highest-value potion
        and consuming its ingredients from the inventory until no more
        potions can be made.

        Args:
            player_stats: Player stats dict with keys:
                - alchemy_skill: int
                - fortify_alchemy: int
                - alchemist_perk: int
                - physician_perk: bool
                - benefactor_perk: bool
                - poisoner_perk: bool
                - seeker_of_shadows: bool
                - purity_perk: bool
            inventory: Inventory instance with available ingredients

        Returns:
            List of Potion objects created (in order of creation)
        """
        potions_made = []

        while not inventory.is_empty():
            # Generate all possible potions from current inventory
            sim = AlchemySimulator(player_stats, inventory.get_available_ingredients())

            # No more valid potions can be made
            if not sim.potions:
                break

            # Select highest-value potion
            best = max(sim.potions, key=lambda p: p.total_value)

            # Try to consume ingredients
            if inventory.consume_recipe(best.ingredient_names):
                potions_made.append(best)
            else:
                # Should not happen if logic is correct, but break to avoid infinite loop
                break

        return potions_made


def main():

    db = IngredientsDatabase()
    alembic = Alembic.from_base_player()

    print("generating inventory...")
    inv = Inventory.generate_normal(db, 20)
    alembic.set_inventory(inv)

    print("printing inventory\n=================\n")
    print(inv)

    print("\ncreating potions...")
    potions = alembic.exhaust_inventory()

    print("printing potions\n================\n")
    for potion in potions:
        print(potion)



if __name__ == "__main__":
    main()
