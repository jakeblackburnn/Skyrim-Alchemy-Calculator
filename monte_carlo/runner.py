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
from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class MonteCarloConfig:
    num_simulations: int = 100
    num_workers: int = 1
    seed: Optional[int] = None
    progress_bar: bool = False
    checkpoints: bool = False
    checkpoint_freq: Optional[int] = 100

class MonteCarloResult:
    pass

class Experiment:

    @abstractmethod
    def run_once(self):
        pass

class MonteCarlo: # main runner object

    def __init__(self, config: MonteCarloConfig):
        self.config = config
        print(f"created mc runner.\nconfig:\n{config}")

    def run(self, experiment: Experiment):
        print("running mc experiment...")
        for exp in range(self.config.num_simulations):
            result = experiment.run_once()
            print(f"[{exp} / {self.config.num_simulations}: {result}")

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
