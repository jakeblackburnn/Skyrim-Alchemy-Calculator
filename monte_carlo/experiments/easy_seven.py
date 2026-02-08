from ..runner import Experiment
from src.inventory import Inventory
from src.alembic import Alembic
from src.player import Player
from src.database import IngredientsDatabase

class EasyExperiment(Experiment):

    def __init__(self, db=IngredientsDatabase(), player=Player(), inv_size=7):
        self.db = db
        self.player = player 
        self.inv_size = inv_size

    def run_once(self, run_idx) -> Dict[str, int]:
        inv = Inventory.generate_normal(self.db, self.inv_size)
        alembic = Alembic(self.db, self.player, inv)
        potions = alembic.exhaust_inventory()

        return {"run_idx": run_idx, "num_potions": len(potions)}
