from monte_carlo.runner import MonteCarlo, MonteCarloConfig, Experiment
from monte_carlo.experiments import TestExperiment

config = MonteCarloConfig()
runner = MonteCarlo(config)
test_experiment = TestExperiment()

# AAHAHAHAHHA
runner.run(test_experiment)
