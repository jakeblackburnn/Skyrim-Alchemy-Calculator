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
class MC_Config:
    num_simulations: int = 1000
    num_workers: int = 1
    seed: Optional[int] = None
    progress_bar: bool = True
    checkpoints: bool = True
    checkpoint_freq: Optional[int] = 100
