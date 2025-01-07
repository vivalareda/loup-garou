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
        self.lovers: List[Player] = []
        self.veto_player = None
        self.player_votes_count: Dict[str, int] = {}
        self.werewolves_alive = 0
        self.villagers_alive = 0
        self.winners = None

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
                self.cupid = player.sid
                role = PlayerRole.WEREWOLF
                self.set_veto_player(player.sid)
                player.role = role
            elif player.name == "carl":
                role = PlayerRole.WITCH
                player.role = role
            else:
                player.role = role

    def set_lovers(self, player1: Player, player2: Player):
        player1.lover_sid = player2.sid
        player2.lover_sid = player1.sid
        self.lovers = [player1, player2]

    def get_lovers(self) -> List[Player]:
        return self.lovers

    def add_pending_death(self, player: Player):
        if player.sid not in self.pending_deaths:
            self.pending_deaths.append(player.sid)

    def remove_pending_death(self, player: Player):
        if player.sid in self.pending_deaths:
            self.pending_deaths.remove(player.sid)

    def set_veto_player(self, player_sid: str):
        self.veto_player = player_sid

    def set_player_vote(self, player_sid: str):
        print("The player voted is : ", player_sid)
        if player_sid in self.player_votes_count:
            self.player_votes_count[player_sid] += 1
        else:
            self.player_votes_count[player_sid] = 1

        dict(
            sorted(self.player_votes_count.items(), key=lambda item: item[1]),
            reverse=True,
        )

    def annouce_death(self, player_sid: str):
        player = self.get_player(player_sid)
        if not player:
            raise ValueError("Invalid target player")
        if player.lover_sid:
            lover = self.get_player(player.lover_sid)
            if lover:
                lover.is_alive = False
        player.is_alive = False

    def get_top_voted_players(self) -> List[str]:
        if not self.player_votes_count:
            return []
        max_votes = next(iter(self.player_votes_count.values()))
        top_players = [
            player
            for player, votes in self.player_votes_count.items()
            if votes == max_votes
        ]
        return top_players

    def get_werewolves_count(self):
        return len(self.get_players_by_role(PlayerRole.WEREWOLF))

    def reset_player_votes(self):
        self.player_votes_count = {}

    def game_over(self):
        werewolves = len(self.get_players_by_role(PlayerRole.WEREWOLF))
        if werewolves == 0:
            self.winners = "Villagers"
            return True
        if werewolves >= self.villagers_alive:
            self.winners = "Werewolves"
            return True
        return False
