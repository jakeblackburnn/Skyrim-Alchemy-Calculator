import csv
import random
from .effect import Effect
from .ingredient import Ingredient

class IngredientsDatabase:
    # Rarity weights for sampling strategies
    RARITY_WEIGHTS = {
        'normal': {
            'common': 1.0,
            'uncommon': 1.0,
            'rare': 1.0,
            'very_rare': 1.0,
            'unique': 1.0
        },
        'random_weighted': {
            'common': 1.0,
            'uncommon': 0.85,
            'rare': 0.7,
            'very_rare': 0.5,
            'unique': 0.3
        }
    }

    # Source type weights for sampling strategies
    # All uniform (1.0) for now - ready for future tuning
    SOURCE_WEIGHTS = {
        'normal': {
            'plant': 1.0,
            'creature': 1.0,
            'fish': 1.0,
            'fungus': 1.0,
            'food': 1.0,
            'crafting': 1.0,
            'misc': 1.0,
            'drug': 1.0
        },
        'random_weighted': {
            'plant': 1.0,
            'creature': 1.0,
            'fish': 1.0,
            'fungus': 1.0,
            'food': 1.0,
            'crafting': 1.0,
            'misc': 1.0,
            'drug': 1.0
        }
    }

    # Inventory size distribution parameters
    INVENTORY_SIZE_PARAMS = {
        'normal': {
            'mean': 35,
            'std': 10,
            'min': 10,
            'max': 70
        },
        'random_weighted': {
            'mean': 35,
            'std': 10,
            'min': 10,
            'max': 70
        }
    }

    # Ingredients excluded from vendor inventories despite rarity classification
    # Note: Some entries may need verification against actual game vendor availability
    VENDOR_BLACKLIST = [
        'Ancestor Moth Wing',        # Dawnguard - rare but quest-specific
        'Chaurus Hunter Antennae',   # Dawnguard - rare but limited availability
        'Crimson Nirnroot',          # Very rare - already excluded by rarity tier
        'Glowing Mushroom',          # Common but blackwater cave-exclusive (verify)
        'Gleamblossom',              # Dawnguard - uncommon but quest-locked
    ]

    # Maps ingredient rarity levels to vendor tier pools
    # very_rare and unique rarities are excluded entirely from vendor inventories
    VENDOR_TIER_ASSIGNMENT = {
        'common': 'common_pool',
        'uncommon': 'uncommon_pool',
        'rare': 'rare_pool',
        'very_rare': 'EXCLUDED',
        'unique': 'EXCLUDED',
    }

    # Vendor tier configuration for Bernoulli sampling
    # Each slot has independent spawn_chance probability of being filled
    # Expected inventory size: (15 + 10 + 5) * 0.75 = 22.5 unique ingredients
    VENDOR_TIERS = {
        'common_pool': {
            'slots': 15,
            'spawn_chance': 0.75,
        },
        'uncommon_pool': {
            'slots': 10,
            'spawn_chance': 0.75,
        },
        'rare_pool': {
            'slots': 5,
            'spawn_chance': 0.75,
        },
    }

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

    def _calculate_inventory_size(self, strategy):
        params = self.INVENTORY_SIZE_PARAMS[strategy]
        size = random.gauss(params['mean'], params['std'])
        return max(params['min'], min(params['max'], int(size)))

    def _calculate_weights(self, ingredients, strategy):
        rarity_weights = self.RARITY_WEIGHTS[strategy]
        source_weights = self.SOURCE_WEIGHTS[strategy]

        weights = []
        for ing in ingredients:
            rarity_weight = rarity_weights.get(ing.rarity, 1.0)
            source_weight = source_weights.get(ing.source, 1.0)
            combined_weight = rarity_weight * source_weight
            weights.append(combined_weight)

        return weights

    def _sample_normal(self, size):
        if size is None:
            size = self._calculate_inventory_size('normal')

        all_ingredients = self.get_all_ingredients()

        # Ensure size doesn't exceed available ingredients
        size = min(size, len(all_ingredients))

        # Uniform random sampling without replacement
        sampled = random.sample(all_ingredients, size)

        # Return ingredient names
        return [ing.name for ing in sampled]

    def _sample_random_weighted(self, size):
        if size is None:
            size = self._calculate_inventory_size('random_weighted')

        all_ingredients = self.get_all_ingredients()
        weights = self._calculate_weights(all_ingredients, 'random_weighted')

        # Use set to track unique selections
        selected_names = set()

        # Iteratively sample until we have desired size or exhaust attempts
        max_attempts = size * 3  # Allow some buffer for deduplication
        attempts = 0

        while len(selected_names) < size and attempts < max_attempts:
            # Sample with replacement, then deduplicate
            remaining = size - len(selected_names)
            batch = random.choices(all_ingredients, weights=weights, k=remaining)
            selected_names.update(ing.name for ing in batch)
            attempts += 1

        # Convert to list (may be slightly under size if duplicates were excessive)
        return list(selected_names)

    def _sample_vendor(self):
        """Generate vendor inventory using game-accurate tiered Bernoulli sampling.

        Returns:
            List[str]: Unique ingredient names (typically 18-27 ingredients)
        """
        # Load all ingredients
        all_ingredients = self.get_all_ingredients()

        # Partition into tier pools with filtering
        common_pool = []
        uncommon_pool = []
        rare_pool = []

        for ing in all_ingredients:
            # Skip blacklisted ingredients
            if ing.name in self.VENDOR_BLACKLIST:
                continue

            # Skip very_rare and unique rarities
            if ing.rarity in ['very_rare', 'unique']:
                continue

            # Assign to tier
            if ing.rarity == 'common':
                common_pool.append(ing.name)
            elif ing.rarity == 'uncommon':
                uncommon_pool.append(ing.name)
            elif ing.rarity == 'rare':
                rare_pool.append(ing.name)

        # Run Bernoulli trials for each tier
        selected_ingredients = []

        # Common tier: 15 slots @ 75%
        for _ in range(self.VENDOR_TIERS['common_pool']['slots']):
            if random.random() < self.VENDOR_TIERS['common_pool']['spawn_chance']:
                if common_pool:
                    selected_ingredients.append(random.choice(common_pool))

        # Uncommon tier: 10 slots @ 75%
        for _ in range(self.VENDOR_TIERS['uncommon_pool']['slots']):
            if random.random() < self.VENDOR_TIERS['uncommon_pool']['spawn_chance']:
                if uncommon_pool:
                    selected_ingredients.append(random.choice(uncommon_pool))

        # Rare tier: 5 slots @ 75%
        for _ in range(self.VENDOR_TIERS['rare_pool']['slots']):
            if random.random() < self.VENDOR_TIERS['rare_pool']['spawn_chance']:
                if rare_pool:
                    selected_ingredients.append(random.choice(rare_pool))

        # Deduplicate and return
        return list(set(selected_ingredients))

    def sample_inventory(self, strategy, size=None):
        valid_strategies = ["normal", "random_weighted", "vendor"]

        if strategy not in valid_strategies:
            raise ValueError(
                f"Invalid strategy '{strategy}'. Must be one of: {valid_strategies}"
            )

        if strategy == "normal":
            return self._sample_normal(size)
        elif strategy == "random_weighted":
            return self._sample_random_weighted(size)
        elif strategy == "vendor":
            return self._sample_vendor()

    def print_self(self):
        """Debug helper to print all ingredients."""
        for name, ingredient in self._ingredients.items():
            print(f"{name}: {ingredient}")





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

