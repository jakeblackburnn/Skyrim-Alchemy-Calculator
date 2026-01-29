Comprehensive Analysis & Recommendations for Monte Carlo Simulation Redesign

  Based on my review of the codebase, here's my comprehensive assessment:

  ---
  1. CURRENT STATE: What the Monte Carlo Simulation Does

  Purpose

  The simulation addresses a critical gameplay question: "Which ingredients are actually valuable in practice, not just in theory?"

  It runs 1000 randomized crafting sessions where:
  - Random inventories are generated (10-50 ingredients)
  - A greedy algorithm crafts potions (always pick highest-value potion)
  - Tracks which ingredients/effects/synergies perform well across runs

  Key Insight

  This distinguishes between:
  - Theoretical value: "Blue Butterfly Wing has high-value effects"
  - Practical value: "Blue Butterfly Wing is rare and its partners are uncommon, so it rarely appears in actual gameplay"

  The robustness score (usage_rate × avg_value_contribution) captures "consistently valuable when it appears."

  ---
  2. CRITICAL PROBLEMS WITH CURRENT IMPLEMENTATION

  A. Code Quality Issues

  Problem 1: Jupyter Notebook as Production Code
  - Logic scattered across 29 cells with no modularity
  - Hard to test, version control, or reuse
  - No clear separation of concerns (simulation vs analysis vs visualization)
  - If it crashes at run 950/1000, you lose everything

  Problem 2: Confusing Metric Definitions
  The code has serious double-counting issues documented in the bug report:

  1. Ingredient value contribution (Bug #3): For a 3-ingredient potion worth 1000g, each ingredient claims the full 1000g contribution
    - Result: Sum of all ingredients' contributions >> actual gold generated
    - Makes absolute numbers meaningless (only relative rankings work)
  2. Synergy pair values (Bug #2): A 3-ingredient potion [A,B,C] worth 1000g credits:
    - Pair (A,B): 1000g
    - Pair (A,C): 1000g
    - Pair (B,C): 1000g
    - Triple-counting the same value

  Problem 3: Performance
  - 1000 runs took 4.7 hours (16,978 seconds)
  - Average 17 seconds per run for ~40 potions
  - Greedy algorithm recreates ALL potions on every iteration (inefficient)
  - Creates redundant Player() objects repeatedly

  Problem 4: Perk Analysis Invalidated
  - Critical bug caused 2000% alchemist perk instead of 100%
  - All perk sensitivity results are invalid (showing 4500%+ ROI when reality is ~150%)
  - Bug is fixed but results not re-run
  - Would take another ~1 hour to regenerate

  B. Design Issues

  Problem 5: Unclear Purpose
  The simulation mixes several distinct questions:
  1. Which ingredients are robust (appear often + used when available)?
  2. Which effects dominate actual crafted potions?
  3. Which ingredient pairs synergize well?
  4. How do perks affect ingredient value?
  5. Which inventory strategy is best?

  These should be separate analyses with clear goals.

  Problem 6: Greedy Algorithm Assumption
  The simulation assumes players always craft the highest-value potion. In reality, players might:
  - Save rare ingredients for specific builds
  - Craft cheap potions first to level up quickly
  - Optimize for weight (value/weight ratio)
  - Hoard specific effects (e.g., Paralysis poisons)

  The current analysis tells you nothing about alternative strategies.

  Problem 7: No Actionable Insights
  Results say "Frost Mirriam has robustness score 5560.9" - what does that mean for gameplay?
  - Should I prioritize collecting it?
  - How much better is it than #10 on the list?
  - What's the expected value if I encounter it?

  Missing: practical guidance for players.

  ---
  3. PROPOSED REDESIGN: Simpler, Clearer, Better

  Philosophy

  Separate concerns into clear modules with single responsibilities.

  New Architecture

  src/
    monte_carlo/
      __init__.py
      simulation.py      # Core simulation runner
      metrics.py         # Metric definitions (clear, no double-counting)
      strategies.py      # Crafting strategies (greedy, level-grind, etc.)
      collectors.py      # Data collection during runs
      analyzer.py        # Post-simulation analysis
      export.py          # JSON/CSV export utilities

  notebooks/
    01_run_simulation.ipynb        # Simple: just run & save results
    02_ingredient_analysis.ipynb   # Explore ingredient metrics
    03_synergy_analysis.ipynb      # Explore synergy pairs
    04_strategy_comparison.ipynb   # Compare crafting strategies
    05_perk_analysis.ipynb         # Perk ROI analysis

  Core Improvements

  1. Fix Metrics - No Double-Counting

  Define clear, non-overlapping metrics:

  # INGREDIENT METRICS (per run)
  - appearances: binary (0 or 1) - was this ingredient in inventory?
  - usage: binary (0 or 1) - was it consumed?
  - quantity_available: int
  - quantity_consumed: int
  - potions_participated: int - how many potions used this ingredient?
  - attributable_value: sum(potion_value / num_ingredients) - fair share
  - total_value_participated: sum(potion_value) - for reference only

  # AGGREGATE (across all runs)
  - appearance_rate: % of runs where ingredient appeared
  - usage_rate: % of appearances where it was used
  - avg_attributable_value: mean attributable value when used
  - robustness_score: usage_rate × avg_attributable_value

  Key change: Use attributable_value (fair share) instead of total_value_participated (inflated).

  2. Modular Simulation Runner

  class MonteCarloRunner:
      def __init__(self, config):
          self.config = config
          self.collectors = [
              IngredientCollector(),
              EffectCollector(),
              SynergyCollector()
          ]

      def run(self, num_runs=1000, checkpoint_every=100):
          """Run simulation with checkpointing"""
          for run_id in range(num_runs):
              # Generate inventory
              inv = self._generate_inventory(run_id)

              # Run strategy
              potions = self.strategy.execute(inv, self.player)

              # Collect data
              for collector in self.collectors:
                  collector.observe(run_id, inv, potions)

              # Checkpoint
              if (run_id + 1) % checkpoint_every == 0:
                  self.save_checkpoint(run_id + 1)

          return self.aggregate_results()

  Benefits:
  - Incremental saves (don't lose progress)
  - Pluggable collectors (easy to add new metrics)
  - Testable components

  3. Multiple Strategies

  class CraftingStrategy(ABC):
      @abstractmethod
      def execute(self, inventory, player) -> List[Potion]:
          pass

  class GreedyValueStrategy(CraftingStrategy):
      """Always craft highest-value potion"""

  class GreedyLevelingStrategy(CraftingStrategy):
      """Maximize XP (craft cheap potions first for more total crafts)"""

  class ValuePerWeightStrategy(CraftingStrategy):
      """Optimize for carry capacity (value/weight ratio)"""

  Benefit: Answer multiple gameplay questions with one simulation framework.

  4. Performance Optimizations

  Current bottleneck: Greedy algorithm regenerates ALL possible potions on every iteration.

  Better approach:
  # Pre-compute potion lookup by ingredients
  potion_cache = {}
  for combo in all_combinations:
      if valid(combo):
          potion_cache[frozenset(combo)] = Potion(combo, player, db)

  # During greedy iteration
  def get_valid_potions(inventory):
      """Only check pre-computed combinations that exist in inventory"""
      valid = []
      for combo, potion in potion_cache.items():
          if all(ing in inventory for ing in combo):
              valid.append(potion)
      return valid

  Expected speedup: 10-20x faster (from 4.7 hours → ~15-30 minutes for 1000 runs)

  5. Clear, Focused Analyses

  Instead of one massive notebook, create focused analysis notebooks:

  Notebook 1: Ingredient Tier List
  - Goal: Rank ingredients for collection priority
  - Metrics: Robustness score, availability, avg value
  - Output: "Top 20 ingredients to prioritize" with gameplay recommendations

  Notebook 2: Synergy Finder
  - Goal: Find best ingredient pairs
  - Metrics: Co-occurrence rate, avg pair value, availability
  - Output: "Keep these pairs together in your inventory"

  Notebook 3: Build Optimizer
  - Goal: Which perks give best ROI for your playstyle?
  - Metrics: Perk ROI by ingredient, total value increase
  - Output: "If you focus on wilderness gathering, prioritize Benefactor perk"

  Notebook 4: Strategy Comparison
  - Goal: Is wilderness gathering better than vendor buying?
  - Metrics: Gold/hour, variance, accessibility
  - Output: "Wilderness gathering earns 5x more but requires exploration"

  ---
  4. SPECIFIC RECOMMENDATIONS

  Immediate Actions (If Keeping Current Code)

  1. Fix double-counting (Bug #2, #3):
    - Change value_contributions to attributable_value = potion_value / num_ingredients
    - Document that old metric is "total value participated" (reference only)
  2. Re-run perk analysis (Bug #1):
    - Perk bug is fixed but results are stale
    - Re-execute cells 14 and 26 to get valid perk ROI data
  3. Add checkpointing:
    - Save results every 100 runs to checkpoint_{n}.json
    - Add recovery logic to resume from checkpoint
  4. Document metrics clearly:
    - Add markdown cell explaining each metric
    - Clarify what "robustness score" means for gameplay

  Long-term Redesign (Recommended)

  1. Move core logic to src/monte_carlo/ (week 1):
    - Create modular classes (runner, collectors, strategies)
    - Add unit tests
    - Implement checkpointing
  2. Optimize performance (week 1):
    - Pre-compute potion cache
    - Remove redundant Player() creation
    - Target: <30 minutes for 1000 runs
  3. Create focused analysis notebooks (week 2):
    - One notebook per gameplay question
    - Clear visualizations
    - Actionable insights
  4. Add new strategies (week 2):
    - Implement leveling-optimized strategy
    - Implement value/weight strategy
    - Compare all strategies
  5. Build gameplay guide (week 3):
    - Export tier lists
    - Create synergy cheat sheet
    - Build perk calculator tool

  ---
  5. EXAMPLE: Better Metric Design

  Current (Confusing)

  # Frost Mirriam
  appearance_rate: 26.1%
  usage_rate: 99.2%
  avg_value_contribution: 5603.9 gold  # INFLATED (sum of full potion values)
  robustness_score: 5560.9  # Meaningless absolute number

  Proposed (Clear)

  # Frost Mirriam
  appearance_rate: 26.1% (appears in ~1 out of 4 runs)
  usage_rate: 99.2% (almost always used when available)
  avg_potions_per_use: 3.2 (typically makes 3 potions when used)
  avg_attributable_value: 1867g (fair share of potion value)
  total_value_participated: 5604g (reference: sum of all potion values)
  robustness_score: 1853 (= usage_rate × avg_attributable_value)

  # GAMEPLAY INSIGHT:
  # "PRIORITY: HIGH - Appears frequently, almost always useful,
  #  contributes ~1867g per use. Excellent wilderness ingredient."

  ---
  6. WHAT MAKES THIS BETTER?

  Clarity

  - One module, one purpose - easy to understand
  - Clear metric definitions - no confusion about double-counting
  - Focused analyses - each notebook answers one question

  Maintainability

  - Modular code - easy to test and modify
  - Version control friendly - proper Python modules
  - Extensible - easy to add new strategies/metrics

  Performance

  - 10-20x faster - pre-computed caches, no redundant work
  - Checkpointing - don't lose progress
  - Incremental - can run small batches and combine

  Usefulness

  - Actionable insights - clear gameplay recommendations
  - Multiple perspectives - different strategies for different playstyles
  - Exportable - tier lists, cheat sheets, tools

  ---
  7. FINAL VERDICT

  Current Code Assessment

  Quality: 4/10 - Works but has serious issues
  - ✅ Core concept is sound (robustness metric is valuable)
  - ✅ Comprehensive tracking (ingredients, effects, synergies)
  - ❌ Major double-counting bugs
  - ❌ Poor code organization (notebook spaghetti)
  - ❌ Slow performance (4.7 hours)
  - ❌ Invalid perk analysis results

  Recommendation: Redesign from scratch with a cleaner architecture.

  What to Keep

  - Robustness metric concept (usage_rate × value)
  - Comparison of inventory strategies
  - Effect co-occurrence heatmap
  - Top performers ranking approach

  What to Change

  - Move logic out of notebook into proper modules
  - Fix double-counting (use attributable value)
  - Optimize performance (potion caching)
  - Create focused analyses instead of one monolith
  - Add multiple crafting strategies
  - Generate actionable gameplay insights
