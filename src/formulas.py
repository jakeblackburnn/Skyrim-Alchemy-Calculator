from player import Player
from effect import Effect, EffectType
import math

def mag(effect, player):

    mag = effect.base_mag # final magnitude is just a multiple of base magnitude
    
    mag *= 4 * (1 + player.alchemy_skill / 200)   # SKILL FACTOR
    mag *= 1 + player.fortify_alchemy / 100       # ENCHANTMENTS FACTOR

    mag *= 1 + (player.alchemist_perk / 100)        # PERK FACTORS
    mag *= 1 + (player.seeker_of_shadows / 100)
    mag *= 1 + (int(effect.is_restore) * player.physician_perk / 100)
    mag *= 1 + (int(effect.is_fortify) * player.benefactor_perk / 100) + (int(effect.is_poison) * player.poisoner_perk / 100)

    return round(mag)

def base_cost(effect):

    if effect.variable_duration:
        return -1
    
    magnitude = mag(effect, Player())
    duration = effect.base_dur

    return math.floor(effect.base_cost * pow(magnitude, 1.1) * pow(duration / 10, 1.1))

def cost(effect, player):
    
    if effect.variable_duration:
        return -1
    magnitude = mag(effect, player)
    duration = effect.base_dur

    return math.floor(effect.base_cost * pow(magnitude, 1.1) * pow(duration / 10, 1.1))



if __name__ == "__main__":
    lv100_player = Player(100)
    op_player = Player(100, 100, 5, True, True, True, True)
    effect = Effect("RiverBetty_DamageHealth", 3, 5, 10, EffectType.POISON)

    op_player.print_self()
    print(mag(effect, op_player))

    print(effect.name, " - base cost:", base_cost(effect), " - lvl100 cost:", cost(effect, lv100_player), " - max acheivable:", cost(effect, op_player))

    

