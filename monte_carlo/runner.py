"""
Monte Carlo Runner Module for ESV Skyrim alchemy analysis with random inventory generation
---

Created by J. Blackburn - Feb 1 2026

**components**: 
    1. monte carlo config class
    2. results class
    3. single simulation function
    4. main runner class
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class MonteCarloConfig:
    num_simulations: int = 1000
    num_workers: int = 1
    seed: Optional[int] = None
    progress_bar: bool = True
    checkpoints: bool = True
    checkpoint_freq: Optional[int] = 100

class MonteCarloResult:
    pass

class AlchemySim:
    # classmethods for different types of simulations?
    pass

class MonteCarlo: # main runner object
    pass


"""
usage example ideas:

config = MonteCarloConfig(
                ...
            )
sim = AlchemySim.vendor_analysis()
mc = MonteCarlo(config)

result: MonteCarloResult = mc.run(sim)

result.save_to_csv()
"""
