from monte_carlo.runner import MonteCarlo, MonteCarloConfig, Experiment
from monte_carlo.experiments.easy_seven import EasyExperiment, EasyResult

config = MonteCarloConfig(num_simulations=1000)
result = EasyResult(config_dict=config.to_dict())
exp    = EasyExperiment()

runner = MonteCarlo(config, result, verbose=True)

runner.run(exp)

result.summary()
