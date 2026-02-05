from .runner import Experiment

class TestExperiment(Experiment):

    def run_once(self):
        return "test experiment ran once."
