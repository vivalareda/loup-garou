"""
Module for managing game segments.

This module defines the `SegmentManager` class and related functionality
for controlling the flow of game segments in the Werewolf game.
"""

from enum import Enum

from colorama import Fore, Style, init
from playsound import playsound

from core.game import Game
from core.roles import PlayerRole

init()


class SegmentType(Enum):
    """Enumeration of game segment types."""

    CUPID = "cupid"
    LOVERS = "lovers"
    WEREWOLF = "werewolf"
    WITCH_HEAL = "witch_heal"
    WITCH_KILL = "witch_kill"
    SEER = "seer"
    DAY = "day"


class SegmentManager:
    """
    Class to manage the progression of game segments.

    Attributes:
        game (Game): The game instance being managed.
        socketio: The SocketIO instance for communication with clients.
    """

    def __init__(self, game: Game, socketio):
        """
        Initialize the SegmentManager.

        Args:
            game (Game): The game instance.
            socketio: The SocketIO instance for communication with clients.
        """
        self.running_hunter_segment = False
        self.first_night = True
        self.game = game
        self.socketio = socketio
        self.current_segment = -1
        self.segment_order = [
            SegmentType.CUPID,
            SegmentType.LOVERS,
            SegmentType.SEER,
            SegmentType.WEREWOLF,
            SegmentType.WITCH_HEAL,
            SegmentType.WITCH_KILL,
            SegmentType.SEER,
            SegmentType.DAY,
        ]
        self.death_queue = []
        self.run_cupid = True

    def play_audio(self, filename):
        """
        Play an audio file.

        Args:
            filename (str): The name of the audio file to play (without extension).
        """
        try:
            playsound(f"./assets/{filename}.mp3")
        except Exception as e:
            print(e)

    def play_start_audio(self, segment):
        """
        Play the start audio for a specific game segment.

        Args:
            segment (SegmentType): The segment type.
        """
        if segment == SegmentType.CUPID:
            self.play_audio("Cupidon/Cupidon-1")
        elif segment == SegmentType.SEER:
            self.play_audio("Seer/Seer-1")
        elif segment == SegmentType.LOVERS:
            self.play_audio("Lovers/Lover-1")
        elif segment == SegmentType.WEREWOLF:
            self.play_audio("Werewolves/Werewolves-1")
        elif segment == SegmentType.WITCH_HEAL:
            self.play_audio("Sorciere-1")
        elif segment == SegmentType.WITCH_KILL:
            self.play_audio("Sorciere-2")

    def start_night(self):
        """Start the night phase of the game."""
        self.current_segment = 0
        print("Starting night")
        # self.play_audio("Intro")  # Uncomment to play the intro audio
        self.run_current_segment()

    def run_current_segment(self):
        """Run the current segment of the game."""
        segment = self.segment_order[self.current_segment]
        if segment == SegmentType.CUPID:
            if self.first_night and self.run_cupid:
                self._run_cupid_segment()
            else:
                self.advance_segment()
        elif segment == SegmentType.LOVERS:
            if self.first_night:
                self._run_lovers_segment()
            else:
                self.advance_segment()
        elif segment == SegmentType.SEER:
            self.advance_segment()
        elif segment == SegmentType.WEREWOLF:
            self.advance_segment()
        elif segment == SegmentType.WITCH_HEAL:
            print("Running witch heal")
            self.advance_segment()
        elif segment == SegmentType.WITCH_KILL:
            self.advance_segment()
        elif segment == SegmentType.DAY:
            self.night_finished()

    def advance_segment(self):
        """Advance to the next segment in the game sequence."""
        print("Current segment is ", self.current_segment)
        if self.current_segment_name() == SegmentType.CUPID and self.first_night:
            self.play_audio("Cupidon/Cupidon-2")
        if self.current_segment == 1 and self.first_night:
            self.play_audio("Lovers/Lover-3")
        if self.current_segment == 2:
            self.play_audio("Werewolves/Werewolves-2")
        if self.current_segment == 4:
            self.play_audio("Sorciere-3")
        if self.current_segment == 5:
            self.play_audio("Wake-up-everyone")
        self.current_segment = (self.current_segment + 1) % len(self.segment_order)
        self.run_current_segment()

    def current_segment_name(self):
        """
        Get the name of the current segment.

        Returns:
            SegmentType: The type of the current segment.
        """
        return self.segment_order[self.current_segment]

    def _run_cupid_segment(self):
        """Run the cupid segment of the game."""
        print("Starting cupid segment")
        self.play_start_audio(SegmentType.CUPID)
        print("Cupid SID", self.game.cupid)
        self.socketio.emit(
            "cupidon_choice",
            {"message": "Choose two players to fall in love"},
            to=self.game.cupid,
        )

    def _run_werewolf_segment(self):
        """Run the werewolf segment of the game."""
        self.play_start_audio(SegmentType.WEREWOLF)
        werewolves = self.game.get_players_by_role(PlayerRole.WEREWOLF)
        for werewolf in werewolves:
            other_werewolves = [w for w in werewolves if w.sid != werewolf.sid]
            self.socketio.emit(
                "werewolf_wake_up",
                {
                    "message": "Choose a victim",
                    "other_werewolves": [w.name for w in other_werewolves],
                },
                to=werewolf.sid,
            )

    def _run_witch_heal_segment(self):
        """Run the witch heal segment of the game."""
        if not self.game.witch_heal_available:
            return
        self.play_start_audio(SegmentType.WITCH_HEAL)
        witch = self.game.get_player_by_role(PlayerRole.WITCH)
        if witch and witch.is_alive and self.game.witch_heal_available:
            last_victim = None
            if self.game.pending_deaths:
                last_victim = self.game.get_player(self.game.pending_deaths[-1])

            if last_victim:
                try:
                    self.socketio.emit(
                        "witch_heal",
                        {
                            "message": "Make your choice",
                            "victim": last_victim.name if last_victim else None,
                        },
                        to=witch.sid,
                    )
                except Exception as e:
                    print(e)

    def _run_witch_kill_segment(self):
        """Run the witch kill segment of the game."""
        if not self.game.witch_kill_available:
            return
        self.play_start_audio(SegmentType.WITCH_KILL)
        witch = self.game.get_player_by_role(PlayerRole.WITCH)
        print("Witch kill available")
        if witch and witch.is_alive and self.game.witch_kill_available:
            try:
                self.socketio.emit(
                    "witch_kill",
                    {"message": "Choose a player to kill"},
                    to=witch.sid,
                )
            except Exception as e:
                print(e)

    def _run_seer_segment(self):
        """Run the seer segment of the game."""
        self.play_start_audio(SegmentType.SEER)
        seer = self.game.get_player_by_role(PlayerRole.SEER)
        print("Seer is", seer)
        if seer:
            self.socketio.emit(
                "seer_choice",
                {"message": "Choose a player to investigate"},
                to=seer.sid,
            )

    def night_finished(self):
        """Mark the night phase as finished and start the day vote."""
        self.first_night = False
        if not self.game.pending_deaths:
            self.play_audio("Night-end/No-deaths")
        else:
            self.play_audio("Night-end/Deaths")
        self.start_day_vote()

    def start_day_vote(self):
        """Start the voting phase during the day."""
        self.socketio.sleep(1)
        print("Starting day vote")
        self.socketio.emit("day_vote")

    def alternative_count_votes(self):
        """Alternative method for processing votes and deaths."""
        self.play_audio("Day-vote/Vote-death")
        self.death_queue = []
        self.awaiting_hunter = False
        self.process_vote_deaths()
        self.process_death_queue()

    def process_vote_deaths(self):
        """Add voted players to the death queue."""
        top_players = self.game.get_top_voted_players()
        for player_sid in top_players:
            player = self.game.get_player(player_sid)
            if player:
                self.queue_death(player, "Vote")
                if player.lover_sid:
                    lover = self.game.get_player(player.lover_sid)
                    if lover:
                        self.queue_death(lover, "Love")

    def queue_death(self, player, cause):
        """
        Add a player to the death queue.

        Args:
            player: Player object to be added to queue.
            cause (str): String indicating cause of death ('Vote', 'Love', 'Hunter', etc.).
        """
        if not any(p.sid == player.sid for p in self.death_queue):
            player.death_cause = cause
            self.death_queue.append(player)

    def process_death_queue(self):
        """Process each death in the queue, checking for special powers."""
        if not self.death_queue:
            self.finish_death_queue_processing()
            return

        current_player = self.death_queue[0]
        print("Processing player", current_player.name)

        if current_player.role == PlayerRole.HUNTER and self.game.hunter_is_alive:
            self.play_audio("Hunter/Hunter")
            self.game.hunter_is_alive = False
            self.socketio.emit(
                "hunter_selection",
                {"message": "Choose a player to kill"},
                to=current_player.sid,
            )
            return

        self._execute_death_sequence(current_player)
        self.death_queue.pop(0)

        self.process_death_queue()

    def _execute_death_sequence(self, player):
        """Handle death execution in the correct announcement order."""
        player.is_alive = False
        if player.role == PlayerRole.WEREWOLF:
            self.game.werewolves_alive -= 1
        else:
            self.game.villagers_alive -= 1

        if player.death_cause == "Vote":
            self.play_audio("Day-vote/Vote-death")
        elif player.death_cause == "Love":
            self.play_audio("Day-vote/Lover")
        elif player.death_cause == "Hunter":
            pass

        try:
            self.socketio.emit("alert_dead", to=player.sid)
        except Exception as e:
            print(f"Error alerting death for {player.name}: {e}")

        if player.role == PlayerRole.WEREWOLF or player.role == PlayerRole.VILLAGER:
            if player.lover_sid:
                self.game.lovers_are_opposited_teams_and_alive = False

        print(f"{player.name} has been killed due to {player.death_cause}")

    def finish_death_queue_processing(self):
        """Finish processing deaths and continue the game."""
        print("Checking remaining deaths in queue...")
        if self.death_queue:
            print(f"Found {len(self.death_queue)} remaining deaths to process")
            self.process_death_queue()
            return

        print("All deaths processed, continuing game...")
        self.awaiting_hunter = False

        is_game_over = self.game.check_game_over()
        if is_game_over:
            case = self.game.winners
            if case == "Villagers":
                self.play_audio("End-game/Villagers-won")
            elif case == "Werewolves":
                self.play_audio("End-game/Werewolves-won")
        else:
            self.advance_segment()

    def check_game_over(self):
        """Check if the game is over and handle end-game logic."""
        is_game_over = self.game.check_game_over()
        if not is_game_over:
            print("Game is not over, next round")
            self.start_night()
        else:
            case = self.game.winners
            if case == "Villagers":
                self.play_audio("End-game/Villagers-won")
            elif case == "Werewolves":
                self.play_audio("End-game/Werewolves-won")

    def _run_lovers_segment(self):
        """Run the lovers segment of the game."""
        self.play_start_audio(SegmentType.LOVERS)
        lovers = self.game.get_lovers()
        player1, player2 = lovers

        self.set_if_lovers_are_opposite_teams(player1, player2)

        if player1.role == PlayerRole.HUNTER or player2.role == PlayerRole.HUNTER:
            self.game.lover_is_hunter = True

        self.socketio.emit("alert_lovers", {"lover": player2.name}, to=player1.sid)
        self.socketio.emit("alert_lovers", {"lover": player1.name}, to=player2.sid)

        self.play_audio("Lovers/Lover-2")

        self.socketio.emit("lover_can_close", to=player1.sid)
        self.socketio.emit("lover_can_close", to=player2.sid)

    def set_if_lovers_are_opposite_teams(self, player1, player2):
        """
        Determine if lovers are on opposite teams.

        Args:
            player1: The first lover.
            player2: The second lover.
        """
        if player1.role == PlayerRole.WEREWOLF and player2.role == PlayerRole.WEREWOLF:
            self.game.lovers_are_opposited_teams_and_alive = True
        if player1.role == PlayerRole.VILLAGER and player2.role == PlayerRole.VILLAGER:
            self.game.lovers_are_opposited_teams_and_alive = True

    def alert_dead_player(self, player_sid):
        """
        Alert a player that they are dead.

        Args:
            player_sid: The socket ID of the player.
        """
        print("Alerting dead player", player_sid)
        try:
            self.socketio.emit("alert_dead", to=player_sid)
        except Exception as e:
            print(e)
