from enum import Enum

class EffectType(Enum):
    FORTIFY = 1
    RESTORE = 2
    POISON = 3

class Effect:

    def __init__(self, name, cost, mag, dur, effect_type, variable_duration=False):

        self.name = name
        self.base_cost = cost
        self.base_mag = mag
        self.base_dur = dur

        self.is_fortify = False
        self.is_restore = False
        self.is_poison = False

        match effect_type:
            case EffectType.FORTIFY:
                self.is_fortify = True
            case EffectType.RESTORE: 
                self.is_restore = True
            case EffectType.POISON:
                self.is_poison = True

        self.variable_duration = variable_duration



if __name__ == "__main__":
    effect = Effect("RiverBetty_DamageHealth", 3, 5, 10, EffectType.POISON)

    print(effect.name, ":", effect.is_poison, effect.base_cost, effect.base_mag, effect.base_dur)
