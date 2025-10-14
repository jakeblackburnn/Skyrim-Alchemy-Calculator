from src.player import Player
from src.alchemy_simulator import AlchemySimulator

player_stats = {
    "alchemy_skill": 39,
    "fortify_alchemy": 17,
    "alchemist_perk": 1,
    "physician_perk": False,
    "benefactor_perk": False,
    "poisoner_perk": False, 
    "seeker_of_shadows": False,
}

ingredients_list = [
    "Bear Claws",
    "Blue Mountain Flower",
    "Butterfly Wing",
    "Wheat",
    "Hanging Moss",
    "Giant's Toe",
    "Creep Cluster",
    "Wheat",
    "Blisterwort",
    "Glowing Mushroom",
]

sim = AlchemySimulator(player_stats, ingredients_list)

sim.print_potions()
