from ..runner import Experiment, MonteCarloResult

class TestExperiment(Experiment):

    def run_once(self):
        return {"value": 100}
