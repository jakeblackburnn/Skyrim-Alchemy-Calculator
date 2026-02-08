from ..runner import Experiment, MonteCarloResult

class TestExperiment(Experiment):

    def run_once(self) -> Dict[str, int]:
        return {"value": 100}
