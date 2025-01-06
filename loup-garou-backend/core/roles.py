from enum import Enum


class PlayerRole(Enum):
    VILLAGER = "villager"
    WEREWOLF = "werewolf"
    WITCH = "witch"
    SEER = "seer"
    HUNTER = "hunter"
    CUPID = "cupid"


class Role:
    def __init__(self, name, description, team):
        self.name = name
        self.description = description
        self.team = team


ROLE_DESCRIPTIONS = {
    PlayerRole.WEREWOLF: Role(
        "Werewolf",
        "Each night, vote with other werewolves to eat a villager",
        "Werewolf",
    ),
    PlayerRole.VILLAGER: Role(
        "Villager", "Vote during the day to eliminate suspected werewolves", "Villager"
    ),
    PlayerRole.SEER: Role(
        "Seer",
        "Each night, check one player to reveal if they are a werewolf",
        "Villager",
    ),
    PlayerRole.CUPID: Role(
        "Cupidon",
        "On the first night, choose two players to fall in love. If one dies, the other dies too.",
        "Villager",
    ),
    PlayerRole.HUNTER: Role(
        "Hunter", "If you die, you can choose to take someone down with you", "Villager"
    ),
    PlayerRole.WITCH: Role(
        "Witch",
        "You have two potions: one to save, one to kill. Use each only once.",
        "Villager",
    ),
}
