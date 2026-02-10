from monte_carlo.runner import MonteCarlo, MonteCarloConfig, Experiment
from monte_carlo.experiments.easy_seven import EasyExperiment, EasyResult

config = MonteCarloConfig(num_simulations=10000)
result = EasyResult(config_dict=config.to_dict())
exp    = EasyExperiment()

runner = MonteCarlo(config, result)

# TODO: time this shit
runner.run(exp)

result.summary()
