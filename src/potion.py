import numpy as np
from .database import IngredientsDatabase, EffectsDatabase
from .effect import Effect
from .player import Player

class Potion:

    def __init__(self, ingredient_names, player, ingredients_db, effects_db):
        # Get all ingredients
        ingredients = [ingredients_db.get_ingredient(name) for name in ingredient_names]

        # Find common effects across ingredients
        all_effect_names = []
        for ingredient in ingredients:
            all_effect_names.extend(ingredient.get_effect_names())

        # Count occurrences and keep only effects shared by 2+ ingredients
        effect_counts = {}
        for effect_name in all_effect_names:
            effect_counts[effect_name] = effect_counts.get(effect_name, 0) + 1
        common_effect_names = {name for name, count in effect_counts.items() if count >= 2}

        # Build Effect objects only for common effects, grouped by effect name
        effect_groups = {}
        for ingredient in ingredients:
            for effect_name in ingredient.get_effect_names():
                if effect_name in common_effect_names:
                    effect = effects_db.ingredient_effect(effect_name, ingredient)
                    if effect_name not in effect_groups:
                        effect_groups[effect_name] = []
                    effect_groups[effect_name].append(effect)

        # Keep only the highest base value effect from each group
        base_effects = []
        for effect_name, effect_list in effect_groups.items():
            base_values = [effect.base_value() for effect in effect_list]
            highest_idx = np.argmax(base_values)
            base_effects.append(effect_list[highest_idx])


        base_costs = [effect.base_value() for effect in base_effects]
        dominant_base = base_effects[np.argmax(base_costs)]

        # Apply Purity perk filtering if player has it
        if player.has_purity:
            if dominant_base.is_poison:
                # Remove beneficial effects (keep only poisons)
                base_effects = [e for e in base_effects if e.is_poison]
            else:
                # Remove harmful effects (keep only beneficial)
                base_effects = [e for e in base_effects if not e.is_poison]


        # Benefactor/poisoner perks only apply to effects in potions/poisons respectively
        # Check if we need to create a modified player (only if there's a perk mismatch)
        needs_modified_player = False
        if dominant_base.is_poison and player.benefactor_perk > 0:
            # Check if any non-poison effects exist
            needs_modified_player = any(not e.is_poison for e in base_effects if e != dominant_base)
        elif not dominant_base.is_poison and player.poisoner_perk > 0:
            # Check if any poison effects exist
            needs_modified_player = any(e.is_poison for e in base_effects if e != dominant_base)

        if needs_modified_player:
            calc_player = Player(
                skill=player.alchemy_skill,
                fortify=player.fortify_alchemy,
                alchemist_perk_level=player.alchemist_perk // 20,
                is_physician=player.physician_perk > 0,
                is_benefactor=(player.benefactor_perk > 0) and not dominant_base.is_poison,
                is_poisoner=(player.poisoner_perk > 0) and dominant_base.is_poison,
                is_seeker=player.seeker_of_shadows > 0,
                has_purity=player.has_purity
            )
        else:
            calc_player = player

        # Realize all effects with player stats (compute once)
        self.realized_effects = [effect.realize(calc_player) for effect in base_effects]
        self.total_value = sum(e.value for e in self.realized_effects)

        self.ingredient_names = ingredient_names

        # Store dominant effect as realized
        self.dominant_effect = next(e for e in self.realized_effects if e.base.name == dominant_base.name)

        # Set potion/poison name based on dominant effect
        prefix = "Poison" if self.dominant_effect.is_poison else "Potion"
        self.name = f"{prefix} of {self.dominant_effect.name}"


    def print_self(self):
        print(f"{self.name}")
        print(f"Ingredients: {', '.join(self.ingredient_names)}")
        print(f"Total Value: {self.total_value} gold")
        print(f"Number of Effects: {len(self.realized_effects)}")
        print("\nEffects:")
        for effect in self.realized_effects:
            print(f"  - {effect.get_description()}")

    def to_dict(self):
        """Serialize potion to JSON-compatible dict for API responses."""
        return {
            "name": self.name,
            "ingredients": self.ingredient_names,
            "total_value": self.total_value,
            "effects": [
                {
                    "name": e.name,
                    "description": e.get_description(),
                    "magnitude": e.magnitude,
                    "duration": e.duration,
                    "value": e.value,
                    "is_poison": e.is_poison
                }
                for e in self.realized_effects
            ]
        }



if __name__ == "__main__":

    # Instantiate databases once
    ingredients_db = IngredientsDatabase()
    effects_db = EffectsDatabase()

    player = Player(skill=40, alchemist_perk_level=1)

    ingredients_names_1 = ["Emperor Parasol Moss", "River Betty"]
    potion_1 = Potion(ingredients_names_1, player, ingredients_db, effects_db)
    potion_1.print_self()

    print("\n" + "="*50 + "\n")

    ingredients_names_2 = ["Blue Mountain Flower", "Hanging Moss"]
    potion_2 = Potion(ingredients_names_2, player, ingredients_db, effects_db)
    potion_2.print_self()
