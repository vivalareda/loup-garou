from dataclasses import dataclass
from enum import Enum


class DeathTrigger(Enum):
    WEREWOLF_KILL = "werewolf_kill"
    WITCH_KILL = "witch_kill"
    VILLAGE_VOTE = "village_vote"
    HUNTER_REVENGE = "hunter_revenge"
    LOVER_DEATH = "lover_death"


@dataclass
class DeathEffect:
    player_sid: str
    trigger: DeathTrigger
    processed: bool = False
