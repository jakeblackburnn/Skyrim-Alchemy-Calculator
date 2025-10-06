class Player:

    def __init__(self, 
                 skill=15, 
                 fortify=0, 
                 alchemist_perk_level=0, 
                 is_physician=False, 
                 is_benefactor=False, 
                 is_poisoner=False, 
                 is_seeker=False,
                 has_purity=False):

        self.alchemy_skill = skill
        self.fortify_alchemy = fortify
        self.has_purity = has_purity

        self.alchemist_perk = 0
        self.physician_perk = 0
        self.benefactor_perk = 0
        self.poisoner_perk = 0
        self.seeker_of_shadows = 0



        for i in range(0, alchemist_perk_level):
            self.alchemist_perk += 20

        if is_physician:
            self.physician_perk += 25

        if is_benefactor:
            self.benefactor_perk += 25

        if is_poisoner:
            self.poisoner_perk += 25

        if is_seeker:
            self.seeker_of_shadows = 10

    @classmethod
    def from_dict(cls, dict):
        return cls(dict["alchemy_skill"],
                   dict["fortify_alchemy"],
                   dict["alchemist_perk"],
                   dict["physician_perk"],
                   dict["benefactor_perk"],
                   dict["poisoner_perk"],
                   dict["seeker_of_shadows"])


    def print_self(self):
        print(self.alchemy_skill, 
              self.fortify_alchemy, 
              self.alchemist_perk, 
              self.physician_perk,
              self.benefactor_perk, 
              self.poisoner_perk, 
              self.seeker_of_shadows)

if __name__ == "__main__":
    player = Player()
    player.print_self()

