class Role:
    def __init__(self, name, description, team):
        self.name = name
        self.description = description
        self.team = team

    def get_role_description(self, role_name):
        return roles[role_name].description


roles = {
    "werewolf": Role(
        "Werewolf",
        "Each night, vote with other werewolves to eat a villager",
        "Werewolf",
    ),
    "villager": Role(
        "Villager", "Vote during the day to eliminate suspected werewolves", "Villager"
    ),
    "seer": Role(
        "Seer",
        "Each night, check one player to reveal if they are a werewolf",
        "Villager",
    ),
    "cupidon": Role(
        "Cupidon",
        "On the first night, choose two players to fall in love. If one dies, the other dies too.",
        "Villager",
    ),
}
