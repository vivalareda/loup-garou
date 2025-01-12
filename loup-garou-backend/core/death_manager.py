# core/death_manager.py
from typing import List

from core.player import Player
from core.roles import PlayerRole


class DeathManager:
    def __init__(self, game):
        self.game = game
        self.pending_deaths: List[str] = []  # List of player_sids
        self.awaiting_special_power = False
        self.queud_deaths = []

    def kill_player(self, player_sid: str):
        """Kill a player and update team counts"""
        player = self.game.get_player(player_sid)
        if player is None:
            print("Player not found")
            return

        player.is_alive = False
        print(f"Player's list is now: {self.game.players}")
        self._update_team_counts(player)
        self.queud_deaths.append(player)

    def handle_kill(self, target_sid: str) -> List[str]:
        """
        Handle a kill action and return list of players who died
        """
        killed_players = []
        target = self.game.get_player(target_sid)

        if target:
            self.kill_player(target_sid)
            killed_players.append(target_sid)

            self._check_special_powers(target)

            if target.lover_sid:
                lover = self.game.get_player(target.lover_sid)
                if lover:
                    self._check_special_powers(target)
                    self.kill_player(lover.sid)
                    killed_players.append(lover.sid)

        return killed_players

    def _update_team_counts(self, player: Player):
        """Update team counts when a player dies"""
        if player.role == PlayerRole.WEREWOLF:
            self.game.werewolves_alive -= 1
        else:
            self.game.villagers_alive -= 1

    def add_pending_death(self, player: Player):
        """Add a player to pending deaths list"""
        if player.sid not in self.pending_deaths:
            self.pending_deaths.append(player.sid)

    def remove_pending_death(self, player: Player):
        """Remove a player from pending deaths list"""
        if player.sid in self.pending_deaths:
            self.pending_deaths.remove(player.sid)

    def _check_special_powers(self, player: Player):
        """
        Handle any special powers when a player dies
        """
        if player.role == PlayerRole.HUNTER:
            print(f"Checking if {player.name} is hunter")
            pass
