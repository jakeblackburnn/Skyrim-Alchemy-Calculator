# Skyrim Alchemy Analysis: Metrics & Monte Carlo Recommendations

## Current Data Model

**Core Classes:**
- `Player`: skill/100, fortify_alchemy/100, perks (Alchemist/Physician/Benefactor/Poisoner/Purity)
- `Ingredient`: name, value, weight, 4 effects (each with mag/dur), rarity, source, DLC
- `Effect`: base_cost, base_mag/dur, type (fortify/restore/poison), variable_duration flag
- `RealizedEffect`: Computed effect with player-scaled magnitude/duration/value
- `Potion`: 2-3 ingredients → shared effects → total value calculation
- `Inventory`: Ingredient quantities with multiple generation strategies (normal, weighted, vendor)

---

## Current Metrics in Notebook

### Effect Metrics (Cell 4)

Located in `monte_carlo.ipynb` cell 4.

1. **count**: Number of ingredients that have this effect
2. **total_value**: Sum of realized effect values across all ingredients (base player)
3. **avg_value**: Mean effect value (`total_value / count`)
4. **frequency**: Proportion of ingredients with this effect (`count / total_ingredients`)
5. **utility**: Combined importance score (`avg_value × frequency`) - balances value and availability

**Interpretation**: Utility identifies effects that are both valuable AND common. High utility = easier to exploit. Example: "Damage Magicka Regen" (utility=25.4) is valuable despite moderate avg_value because it appears in 15 ingredients.

### Ingredient Metrics (Cell 5)

Located in `monte_carlo.ipynb` cell 5.

1. **synergy_at_least_1**: Count of ingredients sharing ≥1 effect
2. **synergy_exactly_2/3/4**: Counts of ingredients sharing exactly 2/3/4 effects
3. **partners_exactly_2/3/4**: Lists of ingredient names for each synergy level (2+ only)
4. **total_value**: Sum of all 4 effect values for this ingredient
5. **avg_utility**: Mean utility score across the ingredient's 4 effects

**Interpretation**: Synergy metrics identify "hub" ingredients with many valid potion combinations. High synergy_exactly_2 = more 2-ingredient potion options. `total_value` measures raw power but ignores weight/rarity.

---

## Key Gaps & Recommended Additions

### Missing Effect Metrics

#### 1. Perk Sensitivity
How much does this effect's value change across perk configurations?

- **Implementation**: Calculate value variance across player archetypes (no perks, poisoner, benefactor, etc.)
- **Why**: Identifies effects with high ROI for specific builds

#### 2. Rarity-Weighted Accessibility
How easy is it to obtain ingredients with this effect?

- **Implementation**: `Σ(1/rarity_weight)` for each ingredient with effect, normalized
- **Why**: Current frequency treats all ingredients equally; rare ingredients are harder to collect

#### 3. Realized Potion Contribution
Average value this effect adds to actual potions (not just solo value)

- **Implementation**: Track effect values in all valid 2/3-ingredient combinations
- **Why**: Effects behave differently in isolation vs. multi-effect potions due to perk interactions

#### 4. Type Distribution Breakdown
- `count_poison`, `count_fortify`, `count_restore` per effect
- **Why**: Purity perk filtering makes type composition critical

#### 5. Multi-Effect Co-occurrence
Which effects commonly appear together in potions?

- **Implementation**: Co-occurrence matrix of effects in valid potion combinations
- **Why**: Identifies natural synergies for potion archetypes

### Missing Ingredient Metrics

#### 1. Value Density
`total_value / weight`

- **Why**: Weight limits matter for carry capacity optimization

#### 2. Rarity-Weighted Synergy
Current synergy doesn't penalize rare partners

- **Implementation**: `Σ(1/partner_rarity_weight)` for each synergy level
- **Why**: A common ingredient with rare-only partners is less useful than one with common partners

#### 3. Best Potion Value
Maximum value achievable with this ingredient in any 2/3-combo

- **Implementation**: `max(potion.value for all valid potions containing ingredient)`
- **Why**: Identifies "star" ingredients for value optimization

#### 4. Versatility Score
Number of valid potion combinations this ingredient enables

- **Implementation**: Count all 2/3-ingredient combos that produce ≥1 shared effect
- **Why**: High versatility = more robust to limited inventories

#### 5. Effect Quality Variance
Not just avg_utility, but std/min/max

- **Why**: Identifies ingredients with 1-2 great effects vs. 4 mediocre ones

#### 6. Source/Rarity Encoded
Currently not included in metrics dict

- **Why**: Critical for Monte Carlo filtering and scenario generation

---

## Adapting Metrics for Monte Carlo Analysis

The Monte Carlo simulation (Cell 7-8) generates random inventories and runs exhaustive potion crafting. **Current gap**: No aggregate statistics across runs.

### Recommended Monte Carlo Metrics

#### 1. Ingredient Importance Under Uncertainty

For each ingredient, track across N simulation runs:

- **Appearance Rate**: % of simulations where ingredient is available
- **Usage Rate**: % of available inventories where ingredient is consumed
- **Avg Potions Produced**: Mean number of potions this ingredient participates in (when available)
- **Avg Value Contribution**: Mean total value from potions containing this ingredient
- **Robustness Score**: `usage_rate × avg_value_contribution` - identifies ingredients that consistently perform well

**Why**: Separates ingredients that are theoretically good (high total_value) from those that are practically good (consistently useful in random inventories).

#### 2. Effect Importance Under Uncertainty

Track across runs:

- **Potion Frequency**: % of crafted potions that include this effect
- **Avg Effect Value in Potions**: Mean realized value when effect appears in potions (vs. theoretical value)
- **Accessibility Under Constraints**: % of inventories where ≥2 ingredients with this effect are available
- **Synergy Realization Rate**: For effects with high co-occurrence, % of runs where both effects appear together

**Why**: Theoretical effect utility assumes infinite ingredients; Monte Carlo shows which effects remain accessible under scarcity.

#### 3. Inventory Composition Metrics

For each simulation:

- **Inventory Rarity Distribution**: % common/uncommon/rare/very_rare/unique
- **Inventory Source Distribution**: % plant/creature/fish/fungus/etc.
- **Total Unique Ingredients**: Inventory size
- **Total Quantity**: Sum of all ingredient counts
- **Theoretical Max Value**: Sum of best possible potions (if we had infinite ingredients)
- **Realized Value**: Total value of potions actually crafted
- **Efficiency Ratio**: `realized_value / theoretical_max_value`

**Why**: Correlates inventory characteristics with outcome quality. Example: Do plant-heavy inventories underperform?

#### 4. Strategy Performance Metrics

Current simulation uses "greedy-basic". Track:

- **Strategy Comparison**: Run multiple strategies on same inventory (greedy-value, greedy-effects, greedy-ingredients)
- **Strategy Robustness**: Variance in performance across inventory types
- **Strategy-Inventory Interaction**: Which strategies excel with rare-heavy vs. common-heavy inventories?

**Why**: Identifies optimal strategies for different player scenarios (vendor shopping, wilderness gathering, etc.).

#### 5. Synergy Pair Performance

For ingredient pairs with `synergy_exactly_2/3/4 > 0`:

- **Co-Appearance Rate**: % of inventories where both ingredients are available
- **Co-Usage Rate**: % of co-appearances where both are used together
- **Avg Pair Value**: Mean potion value when pair is combined
- **Pair Robustness**: `co_usage_rate × avg_pair_value`

**Why**: Pre-computed synergy metrics assume both ingredients are available; Monte Carlo shows which pairs are realistically exploitable.

#### 6. Correlation Analysis

Cross-run statistics:

- **Ingredient Rarity vs. Usage**: Do rare ingredients get used more efficiently when they appear?
- **Inventory Size vs. Efficiency**: Diminishing returns on large inventories?
- **Effect Type Distribution vs. Total Value**: Are poison-heavy inventories more valuable?

**Why**: Reveals non-obvious relationships for optimization guidance.

---

## Implementation Recommendations

### Phase 1: Extend Existing Metrics

Extend `monte_carlo.ipynb` cells 4-5.

Add to effect metrics:
```python
effects_data[effect_name]["perk_sensitivity"] = ...
effects_data[effect_name]["accessibility_weighted"] = ...
```

Add to ingredient metrics:
```python
ingredients_data[ing.name]["value_density"] = total_value / ing.weight
ingredients_data[ing.name]["best_potion_value"] = ...
ingredients_data[ing.name]["versatility"] = ...
```

### Phase 2: Add Monte Carlo Aggregation

Add new cells after simulation loop.

After `results` list is populated:
```python
# Track ingredient performance across runs
ingredient_mc_stats = {}  # {ing_name: {appearances, usages, values, ...}}

# Track effect performance
effect_mc_stats = {}

# Track inventory characteristics
inventory_stats = []

for inv, potions in results:
    # Aggregate metrics here
    ...

# Compute final statistics (means, std, correlations)
```

### Phase 3: Visualization & Insights

Use matplotlib/seaborn for:

- **Scatter**: `theoretical_utility` vs. `mc_robustness_score` (identifies overvalued/undervalued ingredients)
- **Histogram**: Distribution of efficiency ratios across inventory types
- **Heatmap**: Effect co-occurrence matrix in realized potions
- **Box plot**: Value distribution across rarity categories

---

## Specific Code Adaptations for Monte Carlo

### Current Issue

`Inventory.generate_normal()` and `generate_random_weighted()` create inventories, but simulation doesn't track WHICH strategy was used or WHAT the inventory composition was.

### Recommended Changes

#### 1. Store inventory metadata with results

```python
results.append({
    'inventory_meta': {
        'strategy': 'normal',
        'size': inv.unique_items(),
        'total_qty': inv.total_items(),
        'rarity_dist': {...},  # Compute from inv
    },
    'potions': potions_list
})
```

#### 2. Vary inventory strategies across runs

```python
strategies = ['normal', 'random_weighted', 'vendor']
for i in range(1000):
    strategy = random.choice(strategies)
    inv = Inventory.generate_{strategy}(db, size=20)
    ...
```

#### 3. Track ingredient consumption

```python
# Before: results.append(alembic.exhaust_inventory(...))
# After:
initial_inv = alembic.inventory.copy()
potions = alembic.exhaust_inventory(strategy="greedy-basic")
consumed = {name: initial_inv[name] - alembic.inventory.get_quantity(name)
            for name in initial_inv}
results.append({'initial': initial_inv, 'potions': potions, 'consumed': consumed})
```

---

## Summary

### Strengths of Current Metrics

- Effect utility effectively combines value × availability
- Synergy counts capture combinatorial potential
- Avg_utility gives ingredient-level quality score

### Critical Gaps

- No rarity weighting (accessibility overstated)
- No perk sensitivity analysis
- No realized vs. theoretical performance comparison
- No Monte Carlo aggregation (simulation runs in isolation)

### Monte Carlo Priorities

1. Track ingredient/effect **robustness** (consistent performance across random inventories)
2. Measure **synergy realization rates** (theoretical pairs that actually co-occur)
3. Correlate **inventory composition** with outcome quality
4. Compare **strategy performance** under uncertainty
5. Identify **overvalued/undervalued** ingredients (high theory, low practice or vice versa)

---

## Next Steps

1. Implement Phase 1 metric extensions in existing notebook cells
2. Add Monte Carlo aggregation module after simulation loop
3. Create visualization suite for comparative analysis
4. Build correlation analysis pipeline
5. Document findings in player strategy guide

---

## Implementation: Monte Carlo Phase 2 (Completed)

**Date**: 2026-01-13
**Status**: ✅ Complete - 15 new cells added to `monte_carlo.ipynb`

### What Was Implemented

Added comprehensive Monte Carlo aggregation, sensitivity analysis, and visualization suite based on the recommendations above.

#### Section 1: Simulation Infrastructure (Cells 9-11)

**Cell 9 - Monte Carlo Configuration**
- 1000 simulation runs across varied scenarios
- 3 inventory strategies: normal, random_weighted, vendor
- 4 inventory sizes: 10, 20, 35, 50 ingredients
- 3 player archetypes for sensitivity analysis:
  - Novice: skill=15, no perks (baseline)
  - Poisoner: skill=100, poisoner perk active
  - Benefactor: skill=100, benefactor perk active

**Cell 10 - Result Storage Data Structures**
```python
monte_carlo_results = {
    'run_metadata': [],           # Per-run inventory composition and outcomes
    'ingredient_tracking': {},    # Appearance/usage rates and value contributions
    'effect_tracking': {},        # Effect performance in realized potions
    'synergy_tracking': {},       # Ingredient pair co-occurrence and values
    'potion_results': []          # All crafted potions for analysis
}
```

**Cell 11 - Inventory Analysis Helpers**
- `analyze_inventory_composition()`: Extracts rarity/source distributions, total value, unique/total quantities

#### Section 2: Main Monte Carlo Simulation (Cells 12-13)

**Cell 12 - Execute 1000 Monte Carlo Runs**

Implements all recommended Monte Carlo metrics:

**Ingredient Tracking** (per recommendation #1):
- `appearances`: % of runs where ingredient is available ✅
- `usages`: % of appearances where ingredient is consumed ✅
- `quantities_consumed`: Track consumption amounts ✅
- `potions_participated`: Number of potions using this ingredient ✅
- `value_contributions`: Total value from potions with this ingredient ✅

**Effect Tracking** (per recommendation #2):
- `potion_appearances`: Frequency in crafted potions ✅
- `realized_values`: Actual effect values in potions ✅
- `realized_magnitudes/durations`: Track scaling across runs ✅

**Synergy Pair Tracking** (per recommendation #5):
- `co_usages`: Times pair appears together in potions ✅
- `values`: Potion values when pair is combined ✅

**Inventory Composition Tracking** (per recommendation #3):
- Rarity distribution (common/uncommon/rare/very_rare/unique) ✅
- Source distribution (plant/creature/fish/etc.) ✅
- Unique count and total quantity ✅
- Total value of crafted potions ✅

**Cell 13 - Compute Aggregate Statistics**

Calculates final metrics from raw tracking data:

**Ingredient Robustness Metrics**:
- `appearance_rate`: Frequency across all runs
- `usage_rate`: % consumed when available ✅ (from recommendation #1)
- `avg_qty_consumed`: Mean consumption amount
- `avg_value_contribution`: Mean value when used ✅ (from recommendation #1)
- `std_value_contribution`: Variance in performance
- `robustness_score`: `usage_rate × avg_value_contribution` ✅ (exactly as recommended)

**Effect Performance Metrics**:
- `potion_frequency`: % of potions containing effect ✅ (from recommendation #2)
- `avg_realized_value`: Mean value in actual potions ✅ (from recommendation #2)
- `std_realized_value`: Performance variance

**Synergy Performance Metrics**:
- `co_usage_count`: Total times pair was combined
- `avg_pair_value`: Mean potion value for pair ✅ (from recommendation #5)
- `pair_robustness`: `co_usages / total_runs` ✅ (from recommendation #5)

#### Section 3: Sensitivity Analysis (Cells 14-16)

**Cell 14 - Player Perk Sensitivity**
- Tests 5 high-value ingredients (Briar Heart, Butterfly Wing, Blue Mountain Flower, Crimson Nirnroot, Daedra Heart)
- Calculates total ingredient value under each player archetype
- Computes perk ROI: `(benefactor_value - novice_value) / novice_value × 100%`
- Identifies perk-sensitive vs perk-insensitive ingredients ✅ (addresses missing metric: Perk Sensitivity)

**Cell 15 - Strategy Comparison**
- Aggregates performance by inventory strategy (normal/weighted/vendor)
- Compares avg total value, avg potions crafted, std deviation
- Shows min/max values per strategy ✅ (from recommendation #4)

**Cell 16 - Correlation Analysis**
- Builds DataFrame with inventory characteristics vs performance outcomes
- Correlation matrix for:
  - Inventory size vs total value
  - Rarity composition (common_pct, rare_pct) vs value per potion
  - Unique count vs potions crafted
- Reveals non-obvious optimization insights ✅ (from recommendation #6)

#### Section 4: Visualizations (Cells 17-21)

**Cell 17 - Import Libraries**
- Loads matplotlib, seaborn, pandas for visualization

**Cell 18 - Theoretical vs Realized Performance Scatter**
- X-axis: Theoretical utility (from Cell 5: avg_utility)
- Y-axis: Monte Carlo robustness score (from Cell 13)
- Color: Ingredient rarity
- Annotates outliers where MC robustness >> theoretical utility
- **Purpose**: Identifies overvalued/undervalued ingredients ✅ (exactly as recommended in Phase 3)

**Cell 19 - Effect Co-Occurrence Heatmap**
- NxN matrix of effect pairs in realized potions
- Normalized by total potions crafted
- Shows top 30 most frequent effects for readability
- **Purpose**: Reveals natural synergies ✅ (addresses missing metric: Multi-Effect Co-occurrence)

**Cell 20 - Value Distribution Box Plot**
- 3 box plots (normal/weighted/vendor strategies)
- Shows variance and outliers in average potion value
- **Purpose**: Compare strategy robustness ✅ (from recommendation #4)

**Cell 21 - Perk Sensitivity Bar Chart**
- Horizontal bars showing % value increase from novice → benefactor/poisoner
- Separate charts for benefactor and poisoner perks
- **Purpose**: Visual perk ROI analysis ✅ (addresses missing metric: Perk Sensitivity)

#### Section 5: Insights & Export (Cells 22-23)

**Cell 22 - Top Performers Report**
- Top 20 ingredients by robustness score with:
  - Appearance rate, usage rate, avg value contribution
  - Rarity category
- Top 20 synergy pairs by co-usage robustness with:
  - Co-usage count, avg pair value, pair robustness
- **Purpose**: Actionable player recommendations

**Cell 23 - Export Results to JSON**
- Exports all aggregate statistics to `monte_carlo_results.json`
- Includes:
  - `ingredient_robustness`: All robustness metrics
  - `effect_performance`: Effect statistics
  - `synergy_performance`: Pair statistics
  - `run_summary`: Total runs, potions crafted, avg values
- **Purpose**: Enable future analysis, web demo integration, comparative studies

### Metrics Coverage

#### Fully Implemented (from Gap Analysis)

✅ **Ingredient Robustness** (Recommendation #1): appearance_rate, usage_rate, value_contribution, robustness_score
✅ **Effect Performance** (Recommendation #2): potion_frequency, realized_value
✅ **Synergy Pair Performance** (Recommendation #5): co_usage_rate, avg_pair_value, pair_robustness
✅ **Strategy Comparison** (Recommendation #4): Performance across normal/weighted/vendor
✅ **Correlation Analysis** (Recommendation #6): Inventory characteristics vs outcomes
✅ **Perk Sensitivity** (Missing Metric): ROI analysis across player archetypes
✅ **Effect Co-Occurrence** (Missing Metric): Heatmap of realized synergies
✅ **Visualization Suite** (Phase 3): Scatter, heatmap, box plot, bar chart

#### Deferred to Future Phases

⏸️ **Rarity-Weighted Accessibility**: Not yet implemented (requires weighting formula)
⏸️ **Value Density**: `total_value / weight` (simple addition to ingredient metrics)
⏸️ **Best Potion Value**: Max value achievable per ingredient (requires exhaustive combo search)
⏸️ **Versatility Score**: Count of valid combinations per ingredient
⏸️ **Theoretical Max Value**: Ceiling for efficiency ratio calculation
⏸️ **Potion Archetype Clustering**: K-means clustering (planned for Phase 3)

### Testing Recommendations

**Incremental Approach**:
1. Run with `num_runs = 10` first (~10 seconds) to validate tracking logic
2. Inspect `monte_carlo_results` structure to verify data collection
3. Scale to `num_runs = 100` (~2 minutes) for performance testing
4. Full production run with `num_runs = 1000` (~15-20 minutes) for statistical rigor

**Expected Outputs**:
- Console progress updates every 100 runs
- Top 5 ingredients by robustness score preview
- 4 matplotlib visualizations
- `monte_carlo_results.json` export file
- Detailed top 20 performers report

### Key Insights Expected

**Robustness Score separates theory from practice**:
- High theoretical utility + low robustness = overvalued (rare or poor synergies)
- Low theoretical utility + high robustness = hidden gems (common with strong pairs)

**Perk ROI identifies build optimization**:
- Ingredients with >200% ROI for benefactor/poisoner perks are build-critical
- Ingredients with <50% ROI benefit minimally from perks

**Strategy comparison reveals optimal gathering**:
- Vendor inventories likely have lower variance (more predictable)
- Weighted inventories may show higher ceiling (if rare ingredients boost value/potion)

**Correlation analysis uncovers non-obvious patterns**:
- Does rare_pct correlate positively with value_per_potion?
- Does inventory_size show diminishing returns on total_value?

### Future Enhancements (Post-Phase 2)

As noted in user request: **K-means clustering for potion archetypes**
- Cluster on `[num_effects, total_value, avg_ingredient_rarity]`
- Identify archetypes: "rare high-value", "common workhorses", "multi-effect specialists"
- Cluster visualization with accessibility metrics per archetype
- Separate plan to be created after Phase 2 validation
