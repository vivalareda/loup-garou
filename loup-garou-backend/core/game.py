import random
from collections import OrderedDict
from typing import Dict, List, Optional

from core.player import Player
from core.roles import ROLE_DESCRIPTIONS, PlayerRole


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
        self.lovers_are_opposited_teams_and_alive = True
        self.lover_is_hunter = False
        self.reda_sid = None
        self.carl_sid = None

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
        return self.players[sid] if sid in self.players else None

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
        for player, role in zip(self.players.values(), roles_to_assign):
            if player.name == "reda":
                self.reda_sid = player.sid
                role = PlayerRole.WEREWOLF
                self.set_veto_player(player.sid)
                player.role = role
            elif player.name == "carl":
                self.cupid = player.sid
                self.carl_sid = player.sid
                role = PlayerRole.HUNTER
                player.role = role
            else:
                player.role = role
        self.set_teams_count(1)

    def set_teams_count(self, numberOfWerewolves: int):
        self.werewolves_alive = numberOfWerewolves
        self.villagers_alive = len(self.players) - numberOfWerewolves

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
        print("The sid of the player is ", player_sid)
        if player_sid in self.player_votes_count:
            self.player_votes_count[player_sid] += 1
        else:
            self.player_votes_count[player_sid] = 1

        self.player_votes_count = OrderedDict(
            sorted(
                self.player_votes_count.items(), key=lambda item: item[1], reverse=True
            )
        )

    def update_team_counts(self, player: Player):
        if player.role == PlayerRole.WEREWOLF:
            self.werewolves_alive -= 1
        else:
            self.villagers_alive -= 1

    def kill_player(self, player_sid):
        player = self.get_player(player_sid)
        if player is None:
            print("Player not found")
            return
        player.is_alive = False
        print(f"Player's list is now: {self.players}")
        self.update_team_counts(player)

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

    def reset_top_voted_players(self):
        self.player_votes_count = {}

    def get_werewolves_count(self):
        return len(self.get_players_by_role(PlayerRole.WEREWOLF))

    def reset_player_votes(self):
        self.player_votes_count = {}

    def check_game_over(self):
        if self.lovers_are_opposited_teams_and_alive:
            village_count = self.villagers_alive - 1
        else:
            village_count = self.villagers_alive

        if self.werewolves_alive == 0:
            self.winners = "Villagers"
            return True
        if self.werewolves_alive >= village_count:
            self.winners = "Werewolves"
            return True
        return False

    def temporary_function(self):
        if self.reda_sid is None or self.carl_sid is None:
            return
        player1 = self.get_player(self.reda_sid)
        player2 = self.get_player(self.carl_sid)
        self.set_lovers(player1, player2)
