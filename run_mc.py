from monte_carlo.runner import MonteCarlo, MonteCarloConfig, Experiment
from monte_carlo.experiments.easy_seven import EasyExperiment

config = MonteCarloConfig()
runner = MonteCarlo(config)
exp = EasyExperiment()

results = runner.run(exp)

print(results)
