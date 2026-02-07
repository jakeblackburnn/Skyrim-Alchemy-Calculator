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
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class MonteCarloConfig:
    num_simulations: int = 100
    num_workers: int = 1
    seed: Optional[int] = None
    progress_bar: bool = False
    checkpoints: bool = False
    checkpoint_freq: Optional[int] = 100

    def to_dict(self) -> Dict[str, any]:
        return {
            "num_simulations": self.num_simulations,
            "num_workers": self.num_workers,
            "seed": self.seed,
            "checkpoints": self.checkpoints,
            "checkpoint_freq": self.checkpoint_freq,
        }

@dataclass
class MonteCarloResult:
    config_dict: Dict[str, any] = field(default_factory=lambda: {"issue": "no config specified"})
    run_results: List[Dict[str, any]] = field(default_factory=list)

    
    def add_run(self, run: Dict[str, any]):
        self.run_results.append(run)

    def to_dataframe(self):
        pass

    def summary(self):
        print(f"configuration:\n{self.config_dict}\n")
        print(f"results:\n{self.run_results}\n")

class Experiment:
    @abstractmethod
    def run_once(self) -> Dict[str, any]:
        pass

class MonteCarlo: # main runner object

    def __init__(self, config: MonteCarloConfig):
        self.config = config
        print(f"created mc runner.\nconfig:\n{config.to_dict()}")

    def run(self, experiment: Experiment):
        print("running mc experiment...")
        results = MonteCarloResult(config_dict=self.config.to_dict())

        for exp in range(self.config.num_simulations):
            results.add_run(experiment.run_once())

        results.summary()
