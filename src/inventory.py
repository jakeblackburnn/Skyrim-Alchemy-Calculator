from typing import Dict, List
import random
import numpy as np


class Inventory:

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

    # Ingredients excluded from vendor inventories
    VENDOR_BLACKLIST = [
        'Ancestor Moth Wing',
        'Chaurus Hunter Antennae',
        'Crimson Nirnroot',
        'Glowing Mushroom',
        'Gleamblossom',
    ]

    # Maps ingredient rarity levels to vendor tier pools
    VENDOR_TIER_ASSIGNMENT = {
        'common': 'common_pool',
        'uncommon': 'uncommon_pool',
        'rare': 'rare_pool',
        'very_rare': 'EXCLUDED',
        'unique': 'EXCLUDED',
    }

    # Vendor tier configuration for Bernoulli sampling
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

    # Default chi-squared parameters for normal strategy
    QUANTITY_PARAMS_NORMAL = {
        'df': 5,
        'scale': 1.5,
        'min_qty': 1,
        'max_qty': 50
    }

    # Default rarity-based chi-squared parameters for weighted strategy
    QUANTITY_PARAMS_WEIGHTED = {
        'common': {'df': 5, 'scale': 1.5, 'min_qty': 1, 'max_qty': 50},
        'uncommon': {'df': 3, 'scale': 1.2, 'min_qty': 1, 'max_qty': 30},
        'rare': {'df': 1.5, 'scale': 0.7, 'min_qty': 1, 'max_qty': 10},
        'very_rare': {'df': 1, 'scale': 0.5, 'min_qty': 1, 'max_qty': 5},
        'unique': {'df': 1, 'scale': 0.3, 'min_qty': 1, 'max_qty': 3}
    }

    # Default vendor quantity ranges
    VENDOR_QUANTITY_RANGES = {
        'common': (1, 5),
        'uncommon': (1, 3),
        'rare': (1, 2)
    }

    def __init__(self, items: Dict[str, int] = None):
        self._items = items.copy() if items is not None else {}

    def get_available_ingredients(self) -> List[str]:
        return list(self._items.keys())

    def get_quantity(self, name: str) -> int:
        return self._items.get(name, 0)

    def has_ingredient(self, name: str, qty: int = 1) -> bool:
        return self.get_quantity(name) >= qty

    def total_items(self) -> int:
        return sum(self._items.values())

    def unique_items(self) -> int:
        return len(self._items)

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def consume(self, name: str) -> bool:
        if not self.has_ingredient(name, 1):
            return False

        self._items[name] -= 1
        if self._items[name] == 0:
            del self._items[name]

        return True

    def consume_recipe(self, ingredient_names: List[str]) -> bool:
        # Count required quantities
        required = {}
        for name in ingredient_names:
            required[name] = required.get(name, 0) + 1

        # Check availability (fail fast)
        for name, qty in required.items():
            if not self.has_ingredient(name, qty):
                return False

        # All available - consume atomically
        for name, qty in required.items():
            self._items[name] -= qty
            if self._items[name] == 0:
                del self._items[name]

        return True

    @staticmethod
    def _calculate_inventory_size(strategy: str) -> int:
        params = Inventory.INVENTORY_SIZE_PARAMS[strategy]
        size = random.gauss(params['mean'], params['std'])
        return max(params['min'], min(params['max'], int(size)))

    @staticmethod
    def _calculate_weights(ingredients, strategy: str):
        rarity_weights = Inventory.RARITY_WEIGHTS[strategy]
        source_weights = Inventory.SOURCE_WEIGHTS[strategy]

        weights = []
        for ing in ingredients:
            rarity_weight = rarity_weights.get(ing.rarity, 1.0)
            source_weight = source_weights.get(ing.source, 1.0)
            combined_weight = rarity_weight * source_weight
            weights.append(combined_weight)

        return weights

    @staticmethod
    def _sample_chi2_quantity(df, scale, min_qty, max_qty):
        """Sample quantity from chi-squared distribution using numpy.

        Uses Gamma distribution: Chi2(df) = Gamma(df/2, 2)

        Args:
            df: Degrees of freedom (controls mean and variance)
            scale: Multiplier for distribution
            min_qty: Minimum quantity (clamp floor)
            max_qty: Maximum quantity (clamp ceiling)

        Returns:
            int: Sampled quantity in [min_qty, max_qty]
        """
        raw_value = np.random.gamma(df / 2.0, 2.0) * scale
        return max(min_qty, min(max_qty, int(raw_value)))

    @classmethod
    def generate_normal(cls, db, size: int = None, qty_params: dict = None):
        """Generate inventory with uniform random ingredient selection.

        Args:
            db: IngredientsDatabase instance
            size: Number of unique ingredients (default: random from Normal(35, 10))
            qty_params: Custom parameters dict with keys: df, scale, min_qty, max_qty
                       If None, uses class constant QUANTITY_PARAMS_NORMAL

        Returns:
            Inventory: New inventory instance with chi-squared quantity sampling
        """
        if size is None:
            size = cls._calculate_inventory_size('normal')

        all_ingredients = db.get_all_ingredients()

        # Ensure size doesn't exceed available ingredients
        size = min(size, len(all_ingredients))

        # Uniform random sampling without replacement
        sampled = random.sample(all_ingredients, size)

        # Use provided params or default
        params = qty_params if qty_params is not None else cls.QUANTITY_PARAMS_NORMAL

        items = {}
        for ing in sampled:
            qty = cls._sample_chi2_quantity(
                params['df'],
                params['scale'],
                params['min_qty'],
                params['max_qty']
            )
            items[ing.name] = qty

        return cls(items)

    @classmethod
    def generate_random_weighted(cls, db, size: int = None, qty_params: dict = None):
        """Generate inventory with rarity-weighted ingredient selection.

        Args:
            db: IngredientsDatabase instance
            size: Number of unique ingredients (default: random from Normal(35, 10))
            qty_params: Custom rarity-to-params dict (e.g., {'common': {...}, 'rare': {...}})
                       If None, uses class constant QUANTITY_PARAMS_WEIGHTED

        Returns:
            Inventory: New inventory instance with rarity-based chi-squared quantity sampling
        """
        if size is None:
            size = cls._calculate_inventory_size('random_weighted')

        all_ingredients = db.get_all_ingredients()
        weights = cls._calculate_weights(all_ingredients, 'random_weighted')

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

        # Use provided params or default
        params = qty_params if qty_params is not None else cls.QUANTITY_PARAMS_WEIGHTED

        items = {}
        for name in selected_names:
            # Look up ingredient to get rarity
            ing = db.get_ingredient(name)
            rarity = ing.rarity

            # Get rarity-specific params (fallback to 'common' if rarity not in dict)
            rarity_params = params.get(rarity, params.get('common'))

            qty = cls._sample_chi2_quantity(
                rarity_params['df'],
                rarity_params['scale'],
                rarity_params['min_qty'],
                rarity_params['max_qty']
            )
            items[name] = qty

        return cls(items)

    @classmethod
    def generate_vendor(cls, db, qty_params: dict = None):
        """Generate vendor inventory using game-accurate Bernoulli sampling.

        Args:
            db: IngredientsDatabase instance
            qty_params: Custom rarity-to-range dict (e.g., {'common': (1, 5), 'rare': (1, 2)})
                       If None, uses class constant VENDOR_QUANTITY_RANGES

        Returns:
            Inventory: New vendor inventory instance with quantity ranges per rarity
        """
        # Load all ingredients
        all_ingredients = db.get_all_ingredients()

        # Partition into tier pools with filtering
        common_pool = []
        uncommon_pool = []
        rare_pool = []

        for ing in all_ingredients:
            # Skip blacklisted ingredients
            if ing.name in cls.VENDOR_BLACKLIST:
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
        for _ in range(cls.VENDOR_TIERS['common_pool']['slots']):
            if random.random() < cls.VENDOR_TIERS['common_pool']['spawn_chance']:
                if common_pool:
                    selected_ingredients.append(random.choice(common_pool))

        # Uncommon tier: 10 slots @ 75%
        for _ in range(cls.VENDOR_TIERS['uncommon_pool']['slots']):
            if random.random() < cls.VENDOR_TIERS['uncommon_pool']['spawn_chance']:
                if uncommon_pool:
                    selected_ingredients.append(random.choice(uncommon_pool))

        # Rare tier: 5 slots @ 75%
        for _ in range(cls.VENDOR_TIERS['rare_pool']['slots']):
            if random.random() < cls.VENDOR_TIERS['rare_pool']['spawn_chance']:
                if rare_pool:
                    selected_ingredients.append(random.choice(rare_pool))

        # Deduplicate
        unique_names = set(selected_ingredients)

        # Use provided ranges or default
        ranges = qty_params if qty_params is not None else cls.VENDOR_QUANTITY_RANGES

        items = {}
        for name in unique_names:
            # Look up ingredient to get rarity
            ing = db.get_ingredient(name)
            rarity = ing.rarity

            # Get range for this rarity (fallback to (1, 3))
            min_q, max_q = ranges.get(rarity, (1, 3))

            # Sample quantity uniformly from range
            qty = random.randint(min_q, max_q)
            items[name] = qty

        return cls(items)

    def add(self, name: str, qty: int = 1):
        if qty <= 0:
            raise ValueError(f"Quantity must be positive, got {qty}")
        self._items[name] = self._items.get(name, 0) + qty

    @classmethod
    def from_ingredients(cls, ingredient_names: List[str]):
        items = {name: 1 for name in set(ingredient_names)}
        return cls(items)

    def to_ingredient_list(self) -> List[str]:
        return self.get_available_ingredients()

    def copy(self):
        return Inventory(self._items.copy())

    def __repr__(self):
        if self.is_empty():
            return "Inventory(empty)"
        lines = [f"Inventory({self.unique_items()} types, {self.total_items()} total)"]
        for name, qty in self._items.items():
            lines.append(f"  {name}: {qty}")
        return "\n".join(lines)

    def __len__(self):
        """Returns number of unique ingredient types."""
        return self.unique_items()

    def __contains__(self, name: str) -> bool:
        """Support: if 'ingredient' in inventory"""
        return self.has_ingredient(name, qty=1)

    def __getitem__(self, name: str) -> int:
        """Support: quantity = inventory['ingredient']
        Raises KeyError if ingredient not in inventory."""
        qty = self.get_quantity(name)
        if qty == 0:
            raise KeyError(f"Ingredient '{name}' not in inventory")
        return qty

    def __iter__(self):
        """Support: for ingredient_name in inventory"""
        return iter(self._items.keys())

    def __bool__(self):
        """Support: if inventory (False when empty)"""
        return not self.is_empty()
