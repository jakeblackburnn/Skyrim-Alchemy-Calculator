# Skyrim Alchemy Calculator - API Reference

## Overview

The Skyrim Alchemy Calculator `src` module provides a complete Python API for simulating Skyrim's alchemy system. It models players, ingredients, effects, potions, and inventory management with game-accurate formulas for effect scaling and value calculation.

---

## Architecture & Common Workflows

### Module Architecture

The system uses a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────┐
│  Data Layer (CSV Files)                     │
│  - master_ingredients.csv (92+ ingredients) │
│  - effects.csv (55 alchemy effects)         │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  Database Layer (database.py)               │
│  - IngredientsDatabase: O(1) lookups        │
│  - EffectsDatabase: Effect definitions      │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  Domain Models                              │
│  - Player (player.py): Skills & perks       │
│  - Ingredient (ingredient.py): 4 effects    │
│  - Effect (effect.py): Scaling formulas     │
│  - RealizedEffect: Player-computed stats    │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  Inventory Management (inventory.py)        │
│  - Quantity tracking                        │
│  - Generation strategies (vendor/random)    │
│  - Consumption operations                   │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  Potion Crafting (potion.py)                │
│  - 2-3 ingredient combinations              │
│  - Shared effect detection                  │
│  - Purity perk filtering                    │
│  - Value calculation                        │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  Simulation Orchestration                   │
│  - AlchemySimulator (alchemy_simulator.py)  │
│  - Exhaustive combination generation        │
│  - Greedy crafting algorithms               │
└─────────────────────────────────────────────┘
```

### Data Flow Pipeline

**Phase 1: Initialization**
```
CSV Files → Database.__init__() → In-memory dictionaries
         → Player.from_dict(stats) → Player instance
         → Ingredient list → AlchemySimulator.__init__()
```

**Phase 2: Combination Generation**
```
itertools.combinations(ingredients, 2) → Filter by shared effects
itertools.combinations(ingredients, 3) → Filter by shared effects
                                       → List of valid combinations
```

**Phase 3: Potion Creation (per combination)**
```
Potion.__init__(ingredients, player, dbs):
  1. Find common effects (set intersection of ingredient effects)
  2. Retrieve Effect objects from EffectsDatabase
  3. Apply ingredient-specific magnitude/duration overrides
  4. Compute RealizedEffect for each (magnitude/duration scaled by player)
  5. Apply Purity perk filtering (remove opposite effect types)
  6. Apply Benefactor/Poisoner perks to matching effects
  7. Calculate total_value = sum(effect.value for effect in realized_effects)
  → Potion instance
```

### Common Workflows

#### Workflow 1: Simple Potion Discovery
**Use case:** "What potions can I make with these specific ingredients?"

```python
from src.alchemy_simulator import AlchemySimulator

# Define player stats
player_stats = {
    "alchemy_skill": 50,
    "fortify_alchemy": 100,
    "alchemist_perk": 2,      # Rank 0-5 (each adds 20%)
    "physician_perk": True,
    "benefactor_perk": False,
    "poisoner_perk": False,
    "seeker_of_shadows": False,
    "purity_perk": False
}

# Create simulator with ingredient list
ingredients = ["Wheat", "Blue Mountain Flower", "Purple Mountain Flower"]
sim = AlchemySimulator(player_stats, ingredients)

# Access results (sorted by value)
top_potions = sorted(sim.potions, key=lambda p: p.total_value, reverse=True)[:5]
for potion in top_potions:
    print(f"{potion.name}: {potion.total_value} gold")
    print(f"  Ingredients: {', '.join(potion.ingredient_names)}")
```

#### Workflow 2: Inventory Management
**Use case:** "Generate realistic inventory and optimize potion crafting"

```python
from src.database import IngredientsDatabase
from src.inventory import Inventory
from src.alchemy_simulator import AlchemySimulator

# Load database
db = IngredientsDatabase()

# Generate game-accurate vendor inventory
inventory = Inventory.generate_vendor(db)
print(f"Vendor has {inventory.unique_items()} types, {inventory.total_items()} total")

# Create simulator and set inventory
player_stats = {"alchemy_skill": 75, "fortify_alchemy": 120, ...}
sim = AlchemySimulator(player_stats)
sim.set_inventory(inventory)

# Run greedy algorithm (repeatedly craft highest-value potions)
crafted = sim.exhaust_inventory(strategy="greedy-basic")
total_value = sum(p.total_value for p in crafted)
print(f"Crafted {len(crafted)} potions worth {total_value} gold")

# Inventory is consumed, check remaining
print(f"Remaining items: {inventory.total_items()}")
```

#### Workflow 3: Dynamic Player Stats Analysis
**Use case:** "Compare potion values across different skill/perk levels"

```python
from src.alchemy_simulator import AlchemySimulator

ingredients = ["Bear Claws", "Blue Mountain Flower", "Wheat"]
base_stats = {
    "alchemy_skill": 50,
    "fortify_alchemy": 0,
    "alchemist_perk": 0,
    "physician_perk": False,
    "benefactor_perk": False,
    "poisoner_perk": False,
    "seeker_of_shadows": False,
    "purity_perk": False
}

# Analyze perk impact
for perk_rank in range(6):
    stats = base_stats.copy()
    stats["alchemist_perk"] = perk_rank

    sim = AlchemySimulator(stats, ingredients)
    avg_value = sum(p.total_value for p in sim.potions) / len(sim.potions)
    print(f"Alchemist Rank {perk_rank}: avg {avg_value:.1f} gold per potion")
```

### Key Integration Patterns

#### Database Initialization
Databases load CSV files once during initialization and should be reused:

```python
from src.database import IngredientsDatabase, EffectsDatabase

# Load once (reads all CSVs into memory)
ingredients_db = IngredientsDatabase()  # Defaults to data/ directory
effects_db = EffectsDatabase()

# Reuse across many simulations (O(1) lookups)
ingredient = ingredients_db.get_ingredient("Wheat")
ingredient = ingredients_db["Wheat"]  # Alternative syntax (raises KeyError if missing)

# Iterate and check membership
if "Wheat" in ingredients_db:
    for ing in ingredients_db:  # Yields Ingredient objects
        print(ing.name)
```

#### Inventory Operations

**Creation Methods:**
```python
from src.inventory import Inventory
from src.database import IngredientsDatabase

db = IngredientsDatabase()

# Method 1: From dictionary
inv = Inventory({"Wheat": 5, "Blue Mountain Flower": 3})

# Method 2: Generate normal distribution (uniform random selection)
inv = Inventory.generate_normal(db, size=35)

# Method 3: Generate rarity-weighted (biased toward common ingredients)
inv = Inventory.generate_random_weighted(db, size=30)

# Method 4: Generate vendor (game-accurate Bernoulli sampling)
inv = Inventory.generate_vendor(db)

# Method 5: From ingredient list (converts duplicates to quantities)
inv = Inventory.from_ingredients(["Wheat", "Wheat", "Blue Mountain Flower"])
# Result: {"Wheat": 2, "Blue Mountain Flower": 1}
```

**Consumption and State:**
```python
# Check availability
if inv.has_ingredient("Wheat", qty=2):
    inv.consume("Wheat")  # Remove 1

# Atomic recipe consumption (all-or-nothing)
success = inv.consume_recipe(["Wheat", "Blue Mountain Flower", "Wheat"])
# Returns False if any ingredient unavailable (no changes made)

# State checking
inv.total_items()        # Sum of all quantities
inv.unique_items()       # Number of distinct ingredient types
inv.is_empty()          # True if no items
inv.get_available_ingredients()  # List of ingredient names with qty > 0

# Pythonic interface
if inv:                           # Truthy when non-empty
if "Wheat" in inv:               # Check membership
qty = inv["Wheat"]               # Get quantity (raises KeyError if absent)
for name in inv:                 # Iterate ingredient names
    print(f"{name}: {inv[name]}")
```

#### Effect Realization

Effects exist in two forms:
- **Effect**: Base definition from `effects.csv` with default magnitude/duration
- **RealizedEffect**: Player-specific computed values

```python
from src.database import EffectsDatabase
from src.player import Player

effects_db = EffectsDatabase()
player = Player(skill=75, fortify=100, alchemist_perk_level=3)

# Get base effect
effect = effects_db.default_effect("Restore Health")
print(f"Base magnitude: {effect.base_mag}")

# Realize for specific player (scales based on variable_duration flag)
realized = effect.realize(player)
print(f"Realized magnitude: {realized.magnitude}")
print(f"Realized duration: {realized.duration}")
print(f"Gold value: {realized.value}")

# Scaling formula:
# factor = 4 * (1 + skill/200) * (1 + fortify/100) * perk_multipliers
# If variable_duration=False: magnitude scales, duration stays base
# If variable_duration=True: magnitude stays base, duration scales
# value = floor(base_cost * mag^1.1 * (dur/10)^1.1)
```

### Design Decisions

**1. Eager Potion Generation**
- `AlchemySimulator.generate_potions()` is called immediately when ingredients are provided
- Trade-off: Upfront computation cost for instant access to results
- Use case: Interactive UIs benefit from immediate feedback

**2. Database Loading**
- Databases read all CSV files into memory during `__init__`
- O(1) ingredient/effect lookups via dictionaries
- Load once, reuse across thousands of simulations

**3. Purity Perk Application**
- Applied per-potion in `Potion.__init__`, not globally
- Filters out opposite effect types based on dominant effect
- Dominant effect = highest-value effect in potion

**4. Inventory Mutability**
- `Inventory.consume()` and `consume_recipe()` mutate state
- Use `inventory.copy()` to preserve original for comparisons
- `AlchemySimulator.exhaust_inventory()` modifies the inventory in-place

**5. Player Stats Dictionary**
- `Player.from_dict()` converts perk levels to percentage bonuses
- Example: `alchemist_perk_level: 3` → `alchemist_perk: 60%`
- Simplifies JSON serialization for web APIs

---

## Table of Contents

0. [Architecture & Common Workflows](#architecture--common-workflows) - System overview and usage patterns
1. [Player Module](#module-srcplayerpy) - Character skills and perks
2. [Effect Module](#module-srceffectpy) - Alchemical effects and scaling
3. [Ingredient Module](#module-srcingredientpy) - Craftable ingredients
4. [Database Module](#module-srcdatabasepy) - Data loading and access
5. [Inventory Module](#module-srcinventorypy) - Ingredient quantity management
6. [Potion Module](#module-srcpotionpy) - Crafted potions and poisons
7. [Alchemy Simulator Module](#module-srcalchemy_simulatorpy) - Simulation orchestration

---

## Module: `src/player.py`

Defines player character with alchemy skills and perks that affect potion crafting.

### Player

Represents a player character with alchemy skills, perks, and equipment bonuses.

**Constructor:**
```python
Player(skill=15, fortify=0, alchemist_perk_level=0, is_physician=False,
       is_benefactor=False, is_poisoner=False, is_seeker=False, has_purity=False)
```

**Parameters:**
- `skill` (int, optional): Base alchemy skill level (0-100). Default: 15
- `fortify` (int, optional): Fortify Alchemy enchantment bonus value. Default: 0
- `alchemist_perk_level` (int, optional): Rank of Alchemist perk (0-5, each rank adds 20%). Default: 0
- `is_physician` (bool, optional): Whether Physician perk is active (25% bonus to restore potions). Default: False
- `is_benefactor` (bool, optional): Whether Benefactor perk is active (25% bonus to beneficial potions). Default: False
- `is_poisoner` (bool, optional): Whether Poisoner perk is active (25% bonus to poisons). Default: False
- `is_seeker` (bool, optional): Whether Seeker of Shadows perk is active (10% bonus). Default: False
- `has_purity` (bool, optional): Whether Purity perk is active (removes opposite effect types). Default: False

**Attributes:**
- `alchemy_skill` (int): Base alchemy skill value
- `fortify_alchemy` (int): Fortify Alchemy equipment bonus
- `alchemist_perk` (int): Computed alchemist perk bonus (alchemist_perk_level * 20)
- `physician_perk` (int): Physician perk bonus (0 or 25)
- `benefactor_perk` (int): Benefactor perk bonus (0 or 25)
- `poisoner_perk` (int): Poisoner perk bonus (0 or 25)
- `seeker_of_shadows` (int): Seeker perk bonus (0 or 10)
- `has_purity` (bool): Purity perk flag

**Class Methods:**

#### from_dict(dict)
Create Player instance from dictionary.

**Parameters:**
- `dict` (Dict[str, Any]): Dictionary with keys matching constructor parameter names

**Returns:**
- `Player`: New Player instance

**Instance Methods:**

#### print_self()
Print player stats to stdout for debugging.

**Returns:** None (prints to stdout)

**Special Methods:**

#### \_\_repr\_\_()
Return string representation of player with skill, fortify, and perk values.

**Returns:**
- `str`: Formatted string like `"Player(skill=50, fortify=100, alchemist=100%, physician=True, benefactor=True, poisoner=False)"`

---

## Module: `src/effect.py`

Defines alchemical effects with magnitude/duration scaling based on player stats.

### EffectType

Enum for classifying effect types.

**Values:**
- `FORTIFY` (1): Beneficial effect that improves stats (e.g., Fortify Health)
- `RESTORE` (2): Beneficial effect that restores resources (e.g., Restore Health)
- `POISON` (3): Harmful/debilitating effect (e.g., Damage Health)

---

### Effect

Base alchemical effect definition with game formulas for scaling magnitude and duration.

**Constructor:**
```python
Effect(name, mag, dur, cost, effect_type, variable_duration=False, description_template=None)
```

**Parameters:**
- `name` (str): Effect name (e.g., "Damage Health")
- `mag` (int): Base magnitude value
- `dur` (int): Base duration in seconds
- `cost` (float): Base cost multiplier for value calculation
- `effect_type` (EffectType): Effect classification enum value
- `variable_duration` (bool, optional): If True, duration scales with player; magnitude stays fixed. Default: False
- `description_template` (str, optional): Format string with {mag} and {dur} placeholders. Default: None

**Attributes:**
- `name` (str): Effect name
- `base_mag` (int): Base magnitude
- `base_dur` (int): Base duration
- `base_cost` (float): Base cost value
- `is_fortify` (bool): True if effect type is FORTIFY
- `is_restore` (bool): True if effect type is RESTORE
- `is_poison` (bool): True if effect type is POISON
- `variable_duration` (bool): Whether duration scales with player skill
- `description_template` (str | None): Description format template

**Class Methods:**

#### from_csv_line(line)
Parse Effect from CSV line.

**Parameters:**
- `line` (str): CSV line with format: `name,id,base_mag,base_dur,base_cost,type,is_beneficial,varies_duration[,description_template]`

**Returns:**
- `Effect`: Parsed Effect instance

**Instance Methods:**

#### base_value()
Compute effect value with default player (skill=15, no perks).

**Returns:**
- `int`: Gold value with default player

#### value(player)
Compute effect value for specific player using game formulas.

**Parameters:**
- `player` (Player): Player to compute value for

**Returns:**
- `int`: Gold value scaled by player stats

#### realize(player)
Create RealizedEffect with computed stats for this player.

**Parameters:**
- `player` (Player): Player to realize effect for

**Returns:**
- `RealizedEffect`: Realized effect instance with cached magnitude/duration

**Special Methods:**

#### \_\_repr\_\_()
Return string representation with effect name, type, and base stats.

**Returns:**
- `str`: Formatted string like `"Effect('Damage Health', type=Poison, base_mag=10, base_dur=0, base_cost=0.5)"`

---

### RealizedEffect

Computed effect for a specific player, caching magnitude/duration calculations.

**Constructor:**
```python
RealizedEffect(base_effect, player)
```

**Parameters:**
- `base_effect` (Effect): Original effect definition
- `player` (Player): Player to compute stats for

**Attributes:**
- `name` (str): Effect name
- `base` (Effect): Reference to base Effect
- `description_template` (str | None): Description format template
- `magnitude` (int): Computed magnitude for this player
- `duration` (int): Computed duration for this player
- `value` (int): Computed gold value for this player

**Properties:**
- `is_poison` (bool): True if base effect is poison type
- `is_fortify` (bool): True if base effect is fortify type
- `is_restore` (bool): True if base effect is restore type

**Instance Methods:**

#### get_description()
Return formatted description string with magnitude and duration values.

**Returns:**
- `str`: Formatted description (uses template if available, otherwise default format)

**Special Methods:**

#### \_\_repr\_\_()
Return string representation with effect name and computed stats.

**Returns:**
- `str`: Formatted string like `"RealizedEffect('Damage Health', mag=10, dur=0, value=15)"`

---

## Module: `src/ingredient.py`

Defines craftable ingredients with four possible alchemical effects.

### Ingredient

Represents an ingredient with name, value, weight, and up to 4 effects.

**Constructor:**
```python
Ingredient(name, id, value, weight,
           effect1, effect1_mag, effect1_dur,
           effect2, effect2_mag, effect2_dur,
           effect3, effect3_mag, effect3_dur,
           effect4, effect4_mag, effect4_dur,
           dlc, rarity, source)
```

**Parameters:**
- `name` (str): Ingredient name
- `id` (str): Game ID
- `value` (int): Base gold value
- `weight` (float): Weight in inventory units
- `effect1` (str): First effect name
- `effect1_mag` (int): Magnitude for first effect
- `effect1_dur` (int): Duration for first effect
- `effect2` (str): Second effect name
- `effect2_mag` (int): Magnitude for second effect
- `effect2_dur` (int): Duration for second effect
- `effect3` (str): Third effect name
- `effect3_mag` (int): Magnitude for third effect
- `effect3_dur` (int): Duration for third effect
- `effect4` (str): Fourth effect name
- `effect4_mag` (int): Magnitude for fourth effect
- `effect4_dur` (int): Duration for fourth effect
- `dlc` (str): DLC expansion this comes from
- `rarity` (str): Rarity tier (common/uncommon/rare/very_rare/unique)
- `source` (str): Source type (plant/creature/fish/fungus/food/crafting/misc/drug)

**Attributes:**
All constructor parameters are stored as instance attributes.

**Class Methods:**

#### from_csv_line(line)
Parse Ingredient from comma-separated CSV line.

**Parameters:**
- `line` (str): CSV line with all ingredient fields

**Returns:**
- `Ingredient`: Parsed Ingredient instance

**Instance Methods:**

#### get_effect_data(name)
Get magnitude and duration for a named effect.

**Parameters:**
- `name` (str): Effect name to look up

**Returns:**
- `Tuple[int, int] | None`: (magnitude, duration) tuple if found, None otherwise

#### get_effect_names()
Get list of all four effect names.

**Returns:**
- `List[str]`: List of 4 effect names

**Special Methods:**

#### \_\_repr\_\_()
Return string representation with name, value, weight, and all effects.

**Returns:**
- `str`: Formatted string like `"Ingredient('Blue Mountain Flower', value=2, weight=0.1, effects=['Restore Health', 'Fortify Conjuration', 'Fortify Health', 'Damage Magicka Regen'])"`

---

## Module: `src/database.py`

Provides data loading and access for ingredients and effects from CSV files.

### IngredientsDatabase

Loads and provides O(1) access to all ingredients from CSV file.

**Constructor:**
```python
IngredientsDatabase(data_dir="data")
```

**Parameters:**
- `data_dir` (str, optional): Directory containing `master_ingredients.csv`. Default: "data"

**Instance Methods:**

#### get_ingredient(name)
Lookup ingredient by name with O(1) complexity.

**Parameters:**
- `name` (str): Ingredient name

**Returns:**
- `Ingredient | None`: Ingredient instance if found, None otherwise

#### get_all_ingredients()
Get list of all loaded ingredients.

**Returns:**
- `List[Ingredient]`: All ingredients from database

#### sample_inventory(strategy, size=None)
**DEPRECATED** - Use `Inventory.generate_*()` methods instead. Will be removed in v2.0.

**Parameters:**
- `strategy` (str): Sampling strategy ('normal', 'random_weighted', or 'vendor')
- `size` (int, optional): Number of ingredients (ignored for 'vendor' strategy)

**Returns:**
- `List[str]`: List of ingredient names

**Migration:**
- Old: `db.sample_inventory("vendor")`
- New: `Inventory.generate_vendor(db).get_available_ingredients()`

**Special Methods:**

#### \_\_repr\_\_()
Return string showing number of loaded ingredients.

**Returns:**
- `str`: Formatted string like `"IngredientsDatabase(92 ingredients loaded)"`

#### \_\_len\_\_()
Return total number of ingredients in database.

**Returns:**
- `int`: Ingredient count

**Usage:** `len(db)`

#### \_\_contains\_\_(name)
Check if ingredient exists in database.

**Parameters:**
- `name` (str): Ingredient name

**Returns:**
- `bool`: True if ingredient exists

**Usage:** `if 'Blue Mountain Flower' in db:`

#### \_\_getitem\_\_(name)
Get ingredient by name using bracket notation.

**Parameters:**
- `name` (str): Ingredient name

**Returns:**
- `Ingredient`: Ingredient instance

**Raises:**
- `KeyError`: If ingredient not found

**Usage:** `ingredient = db['Blue Mountain Flower']`

**Note:** Alternative to `get_ingredient()` which returns None on miss. Use this when you expect the ingredient to exist.

#### \_\_iter\_\_()
Iterate over all ingredients in database.

**Yields:**
- `Ingredient`: Ingredient objects (not names)

**Usage:** `for ingredient in db:`

---

### EffectsDatabase

Loads and provides access to effects from CSV file.

**Constructor:**
```python
EffectsDatabase(data_dir="data")
```

**Parameters:**
- `data_dir` (str, optional): Directory containing `effects.csv`. Default: "data"

**Instance Methods:**

#### default_effect(name)
Get base Effect definition by name.

**Parameters:**
- `name` (str): Effect name

**Returns:**
- `Effect | None`: Effect instance if found, None otherwise

#### ingredient_effect(effect_name, ingredient)
Get Effect for specific ingredient using ingredient's magnitude/duration overrides.

**Parameters:**
- `effect_name` (str): Effect name to look up
- `ingredient` (Ingredient): Ingredient providing the effect

**Returns:**
- `Effect | None`: Effect with ingredient-specific mag/dur values, or None if not found

---

## Module: `src/inventory.py`

Manages ingredient quantities and provides inventory generation strategies.

### Inventory

Manages ingredient quantities with methods for consumption, addition, and generation.

**Constructor:**
```python
Inventory(items=None)
```

**Parameters:**
- `items` (Dict[str, int], optional): Dictionary mapping ingredient names to quantities. Default: None (empty inventory)

**Class Constants:**

- `RARITY_WEIGHTS` (Dict): Rarity weights for each sampling strategy
- `SOURCE_WEIGHTS` (Dict): Source type weights for each sampling strategy
- `INVENTORY_SIZE_PARAMS` (Dict): Size distribution parameters (mean, std, min, max)
- `VENDOR_BLACKLIST` (List[str]): Ingredients never sold by vendors
- `VENDOR_TIER_ASSIGNMENT` (Dict): Maps rarity to vendor tier
- `VENDOR_TIERS` (Dict): Vendor tier configuration (slots, spawn_chance)
- `QUANTITY_PARAMS_NORMAL` (Dict): Chi-squared parameters for normal strategy
- `QUANTITY_PARAMS_WEIGHTED` (Dict): Rarity-specific chi-squared parameters
- `VENDOR_QUANTITY_RANGES` (Dict): Vendor quantity ranges by rarity

**Instance Methods:**

#### get_available_ingredients()
Get list of all ingredient names in inventory.

**Returns:**
- `List[str]`: List of ingredient names

#### get_quantity(name)
Get quantity of specific ingredient.

**Parameters:**
- `name` (str): Ingredient name

**Returns:**
- `int`: Quantity (0 if not present)

#### has_ingredient(name, qty=1)
Check if inventory has at least qty of ingredient.

**Parameters:**
- `name` (str): Ingredient name
- `qty` (int, optional): Minimum quantity required. Default: 1

**Returns:**
- `bool`: True if inventory has at least qty

#### total_items()
Get sum of all quantities.

**Returns:**
- `int`: Total item count across all ingredients

#### unique_items()
Get count of unique ingredients.

**Returns:**
- `int`: Number of unique ingredient types

#### is_empty()
Check if inventory has no items.

**Returns:**
- `bool`: True if empty

#### consume(name)
Remove 1 of ingredient from inventory.

**Parameters:**
- `name` (str): Ingredient name

**Returns:**
- `bool`: True if consumed successfully, False if not available

#### consume_recipe(ingredient_names)
Atomically consume all ingredients in list.

**Parameters:**
- `ingredient_names` (List[str]): Ingredient names to consume (may have duplicates)

**Returns:**
- `bool`: True if all consumed successfully, False if any unavailable (no changes if False)

#### add(name, qty=1)
Add quantity to ingredient.

**Parameters:**
- `name` (str): Ingredient name
- `qty` (int, optional): Quantity to add (must be positive). Default: 1

**Raises:**
- `ValueError`: If qty <= 0

#### to_ingredient_list()
Get list of available ingredient names (alias for get_available_ingredients).

**Returns:**
- `List[str]`: List of ingredient names

#### copy()
Create independent copy of inventory.

**Returns:**
- `Inventory`: New inventory with copied items dict

**Class Methods:**

#### generate_normal(db, size=None, qty_params=None)
Generate inventory with uniform random ingredient selection and chi-squared quantity distribution.

**Parameters:**
- `db` (IngredientsDatabase): Database to sample from
- `size` (int, optional): Number of unique ingredients. Default: random from Normal(35, 10)
- `qty_params` (Dict, optional): Custom parameters (df, scale, min_qty, max_qty). Default: QUANTITY_PARAMS_NORMAL

**Returns:**
- `Inventory`: New inventory instance

#### generate_random_weighted(db, size=None, qty_params=None)
Generate inventory biased toward common rarities with rarity-specific quantity distributions.

**Parameters:**
- `db` (IngredientsDatabase): Database to sample from
- `size` (int, optional): Number of unique ingredients. Default: random from Normal(35, 10)
- `qty_params` (Dict, optional): Custom rarity-to-params mapping. Default: QUANTITY_PARAMS_WEIGHTED

**Returns:**
- `Inventory`: New inventory instance

#### generate_vendor(db, qty_params=None)
Generate game-accurate vendor inventory using Bernoulli sampling per tier.

**Parameters:**
- `db` (IngredientsDatabase): Database to sample from
- `qty_params` (Dict, optional): Custom rarity-to-range mapping. Default: VENDOR_QUANTITY_RANGES

**Returns:**
- `Inventory`: New vendor inventory instance

#### from_ingredients(ingredient_names)
Create inventory from ingredient list with qty=1 for each.

**Parameters:**
- `ingredient_names` (List[str]): Ingredient names

**Returns:**
- `Inventory`: New inventory with each ingredient at qty=1

**Special Methods:**

#### \_\_repr\_\_()
Return string representation with unique/total counts and items preview.

**Returns:**
- `str`: Formatted string showing inventory summary and first 5 items

**Example:** `"Inventory(15 types, 47 total)\n  Items: {'Blue Mountain Flower': 3, 'Wheat': 5, ...}..."`

#### \_\_len\_\_()
Return number of unique ingredient types.

**Returns:**
- `int`: Unique ingredient count (same as `unique_items()`)

**Usage:** `len(inventory)`

#### \_\_contains\_\_(name)
Check if ingredient is in inventory with quantity >= 1.

**Parameters:**
- `name` (str): Ingredient name

**Returns:**
- `bool`: True if inventory has at least 1 of ingredient

**Usage:** `if 'Blue Mountain Flower' in inventory:`

#### \_\_getitem\_\_(name)
Get quantity of ingredient using bracket notation.

**Parameters:**
- `name` (str): Ingredient name

**Returns:**
- `int`: Quantity of ingredient

**Raises:**
- `KeyError`: If ingredient not in inventory (qty=0)

**Usage:** `qty = inventory['Blue Mountain Flower']`

**Note:** Alternative to `get_quantity()` which returns 0 for missing ingredients. Use this when you expect the ingredient to exist.

#### \_\_iter\_\_()
Iterate over ingredient names in inventory.

**Yields:**
- `str`: Ingredient names (not Ingredient objects)

**Usage:** `for name in inventory:`

#### \_\_bool\_\_()
Check if inventory is non-empty.

**Returns:**
- `bool`: False when empty, True otherwise

**Usage:** `if inventory:` or `if not inventory:`

---

## Module: `src/potion.py`

Defines crafted potions and poisons with ingredients and effects.

### Potion

Represents a crafted potion/poison with 2-3 ingredients, computed effects, and value.

**Constructor:**
```python
Potion(ingredient_names, player, ingredients_db, effects_db)
```

**Parameters:**
- `ingredient_names` (List[str]): 2-3 ingredient names
- `player` (Player): Character crafting the potion
- `ingredients_db` (IngredientsDatabase): Ingredient database reference
- `effects_db` (EffectsDatabase): Effect database reference

**Raises:**
- `ValueError`: If ingredient count not 2 or 3
- `ValueError`: If no common effects found among ingredients
- `ValueError`: If any ingredient doesn't share effects with others

**Attributes:**
- `name` (str): Generated name in format "Potion/Poison of [dominant_effect_name]"
- `ingredient_names` (List[str]): Input ingredient names
- `ingredients_list` (List[Ingredient]): Ingredient objects used
- `realized_effects` (List[RealizedEffect]): All effects in potion
- `total_value` (int): Sum of all effect values
- `dominant_effect` (RealizedEffect): Highest-value effect

**Properties:**

- `value` (int): Alias for total_value
- `num_ingredients` (int): Number of ingredients (2 or 3)
- `num_effects` (int): Number of realized effects
- `is_poison` (bool): True if dominant effect is harmful
- `is_beneficial` (bool): True if dominant effect is helpful
- `effect_names` (List[str]): Names of all effects in potion
- `effects` (List[RealizedEffect]): All realized effects
- `ingredients` (List[Ingredient]): All ingredient objects used

**Instance Methods:**

#### print_self()
**DEPRECATED** - Use `print(potion)` or `str(potion)` instead.

Print potion details to stdout for debugging.

**Returns:** None (prints to stdout)

#### to_dict()
Serialize potion to JSON-compatible dictionary.

**Returns:**
- `Dict`: Dictionary with keys: name, ingredients, total_value, effects (array of effect dicts)

**Special Methods:**

#### \_\_repr\_\_()
Return string representation with potion name, ingredients, and value.

**Returns:**
- `str`: Multi-line formatted string

**Example:**
```
Potion of Restore Health
Ingredients: Blue Mountain Flower, Wheat
Value: 15
```

**Usage:** `print(potion)` or `str(potion)`

---

## Module: `src/alchemy_simulator.py`

Main orchestrator for potion crafting simulation and inventory management.

### AlchemySimulator

Orchestrates player, ingredients, databases, and potion generation with simulation strategies.

**Constructor:**
```python
AlchemySimulator(player_stats, ingredients_list=None)
```

**Parameters:**
- `player_stats` (Dict): Player stats dictionary with keys:
  - `alchemy_skill` (int)
  - `fortify_alchemy` (int)
  - `alchemist_perk` (int)
  - `physician_perk` (bool)
  - `benefactor_perk` (bool)
  - `poisoner_perk` (bool)
  - `seeker_of_shadows` (bool)
  - `purity_perk` (bool)
- `ingredients_list` (List[str], optional): Initial ingredient names. Default: None

**Attributes:**
- `ingredients_list` (List[str] | None): Current available ingredient names
- `player` (Player): Current player instance
- `potions` (List[Potion]): Generated valid potions
- `ingredients_db` (IngredientsDatabase): Cached ingredient database
- `effects_db` (EffectsDatabase): Cached effects database

**Class Methods:**

#### from_base_player(ingredients_list=None)
Create simulator with default player (skill=15, no perks).

**Parameters:**
- `ingredients_list` (List[str], optional): Initial ingredient names. Default: None

**Returns:**
- `AlchemySimulator`: New simulator instance

#### greedy_potionmaking(player_stats, inventory)
Static method to run greedy algorithm consuming inventory.

**Parameters:**
- `player_stats` (Dict): Player stats dictionary
- `inventory` (Inventory): Inventory instance to consume

**Returns:**
- `List[Potion]`: List of potions created in order

**Instance Methods:**

#### generate_potions()
Generate all valid 2-3 ingredient potion combinations from current ingredient list.

**Returns:** None (updates self.potions)

#### print_potions()
Print all potions sorted by value to stdout.

**Returns:** None (prints to stdout)

#### update_player(player_stats)
Update player and regenerate potions.

**Parameters:**
- `player_stats` (Dict): New player stats dictionary

**Returns:** None

#### add_ingredient(ingredient_name)
Add ingredient to list and regenerate potions.

**Parameters:**
- `ingredient_name` (str): Ingredient name to add

**Returns:** None

#### remove_ingredient(ingredient_name)
Remove ingredient from list and regenerate potions.

**Parameters:**
- `ingredient_name` (str): Ingredient name to remove

**Returns:** None

#### set_inventory(inventory)
Set Inventory object and regenerate potions from available ingredients.

**Parameters:**
- `inventory` (Inventory): Inventory instance

**Raises:**
- `TypeError`: If inventory is not an Inventory instance

**Returns:** None

#### exhaust_inventory(strategy="greedy-basic")
Run potion-making strategy that consumes current inventory.

**Parameters:**
- `strategy` (str, optional): Algorithm to use ("greedy-basic" supported). Default: "greedy-basic"

**Returns:**
- `List[Potion]`: List of potions created in order

**Raises:**
- `ValueError`: If no inventory set (call set_inventory first)
- `ValueError`: If unknown strategy specified

#### delete_inventory()
Clear current inventory and reset potion state.

**Returns:** None

---

*API Reference generated for Skyrim Alchemy Calculator src module - January 2026*
