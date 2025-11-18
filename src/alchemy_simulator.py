from itertools import combinations
from .player import Player
from .potion import Potion
from .database import IngredientsDatabase, EffectsDatabase

class AlchemySimulator:

    def __init__(self, player_stats, ingredients_list):
        self.ingredients_list = ingredients_list
        self.player = Player.from_dict(player_stats)
        self.ingredients_db = IngredientsDatabase()
        self.effects_db = EffectsDatabase()

        self.generate_potions()

    @classmethod
    def from_base_player(cls, ingredients_list):
        """Create an AlchemySimulator with a default Player (skill=15, no perks)."""
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
        self.generate_potions()

    def add_ingredient(self, ingredient_name):
        # check that ingredient doesnt already exist
        self.generate_potions()

    def remove_ingredient(self, ingredient_name):
        # check that ingredient is in ingredients list 
        self.generate_potions()

