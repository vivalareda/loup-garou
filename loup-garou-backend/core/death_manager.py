from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from core.death_types import DeathEffect, DeathTrigger
from core.roles import PlayerRole


class DeathManager:
    def __init__(self, game, segment_manager):
        self.game = game
        self.pending_deaths: List[DeathEffect] = []
        self.death_queue: List[DeathEffect] = []
        self.segment_manager = segment_manager

    def queue_death(self, player_sid: str, trigger: DeathTrigger):
        """Add a death to the queue with its trigger type"""
        death = DeathEffect(player_sid=player_sid, trigger=trigger)
        self.death_queue.append(death)

    def process_death_queue(self) -> List[str]:
        """Process all queued deaths and return list of killed players"""
        killed_players = []

        while self.death_queue:
            death = self.death_queue.pop(0)
            if death.processed:
                continue

            player = self.game.get_player(death.player_sid)
            if not player or not player.is_alive:
                continue

            self.game.kill_player(death.player_sid)
            killed_players.append(death.player_sid)
            death.processed = True

            self._handle_special_effects(player, death.trigger)

        return killed_players

    def _handle_special_effects(self, player, trigger: DeathTrigger):
        """Handle special effects when a player dies (hunter revenge, lover deaths)"""

        if player.lover_sid:
            lover = self.game.get_player(player.lover_sid)
            if lover and lover.is_alive:
                self.queue_death(lover.sid, DeathTrigger.LOVER_DEATH)

        if player.role == PlayerRole.HUNTER and trigger != DeathTrigger.HUNTER_REVENGE:
            self._trigger_hunter_revenge(player)

    def _trigger_hunter_revenge(self, hunter) -> None:
        """Pause death processing and trigger hunter revenge selection"""
        self.segment_manager.running_hunter_segment = True
        self.game.socketio.emit(
            "hunter_selection", {"message": "Choose a player to kill"}, to=hunter.sid
        )

    def handle_witch_heal(self):
        """
        Handle witch healing action. Removes the most recent death and its related deaths
        (like lover deaths) from the queue.
        """
        if not self.death_queue:
            return

        for death in reversed(self.death_queue):
            if death.trigger not in [DeathTrigger.LOVER_DEATH]:
                victim = self.game.get_player(death.player_sid)

                self.death_queue.remove(death)

                if victim and victim.lover_sid:
                    lover_deaths = [
                        d for d in self.death_queue if d.player_sid == victim.lover_sid
                    ]
                    for lover_death in lover_deaths:
                        self.death_queue.remove(lover_death)

                break

    def handle_hunter_revenge(self, target_sid: str):
        """Process hunter's revenge kill"""
        self.queue_death(target_sid, DeathTrigger.HUNTER_REVENGE)
        killed_players = self.process_death_queue()
        self.game.segment_manager.running_hunter_segment = False
        return killed_players

    def check_game_over(self) -> bool:
        """Check if the game is over after deaths are processed"""
        if self.game.werewolves_alive == 0:
            self.game.winners = "Villagers"
            return True
        if self.game.werewolves_alive >= self.game.villagers_alive:
            self.game.winners = "Werewolves"
            return True
        return False
