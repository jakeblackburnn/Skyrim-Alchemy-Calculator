from monte_carlo.runner import MonteCarlo, MonteCarloConfig, Experiment
from monte_carlo.experiments.test import TestExperiment

config = MonteCarloConfig()
runner = MonteCarlo(config)
test_experiment = TestExperiment()

runner.run(test_experiment)
