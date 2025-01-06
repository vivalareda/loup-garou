import random
from typing import Dict, List, Optional

from .player import Player
from .roles import ROLE_DESCRIPTIONS, PlayerRole


class Game:
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.pending_deaths: List[str] = []
        self.witch_heal_available = True
        self.witch_kill_available = True

    def add_player(self, name: str, sid: str) -> Player:
        player = Player(name=name, sid=sid)
        self.players[sid] = player
        return player

    def add_mock_players(self, count: int):
        mock_names = ["Alice", "Bob", "Charlie", "Eve"]
        for i, name in enumerate(mock_names[:count]):
            mock_sid = f"mock_{i}"
            self.add_player(name, mock_sid)

    def get_player(self, sid: str) -> Optional[Player]:
        return self.players.get(sid)

    def get_player_by_role(self, role: PlayerRole) -> Optional[Player]:
        return next((p for p in self.players.values() if p.role == role), None)

    def get_players_by_role(self, role: PlayerRole) -> List[Player]:
        return [p for p in self.players.values() if p.role == role]

    def assign_roles(self):
        # TODO: Uncomment werewolves and increate number to 5, removed to assign to specific player for testing
        num_players = len(self.players)
        roles_to_assign = [
            # PlayerRole.WEREWOLF,
            # PlayerRole.WEREWOLF,
            # PlayerRole.WITCH,
            PlayerRole.SEER,
            PlayerRole.CUPID,
        ] + [PlayerRole.VILLAGER] * (num_players - 2)

        random.shuffle(roles_to_assign)
        print("All players : ", self.players.values())
        for player, role in zip(self.players.values(), roles_to_assign):
            if player.name == "reda":
                role = PlayerRole.WEREWOLF
                player.role = role
            elif player.name == "carl":
                role = PlayerRole.WITCH
                player.role = role
            else:
                player.role = role

    def set_lovers(self, player1: Player, player2: Player):
        player1.lover_sid = player2.sid
        player2.lover_sid = player1.sid

    def add_pending_death(self, player: Player):
        if player.sid not in self.pending_deaths:
            self.pending_deaths.append(player.sid)

    def remove_pending_death(self, player: Player):
        if player.sid in self.pending_deaths:
            self.pending_deaths.remove(player.sid)
