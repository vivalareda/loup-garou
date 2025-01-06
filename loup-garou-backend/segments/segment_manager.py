# segments/segment_manager.py
from enum import Enum

from playsound import playsound

from core.roles import PlayerRole


class SegmentType(Enum):
    CUPID = "cupid"
    LOVERS = "lovers"
    WEREWOLF = "werewolf"
    WITCH_HEAL = "witch_heal"
    WITCH_KILL = "witch_kill"
    SEER = "seer"


class SegmentManager:
    def __init__(self, game, socketio):
        self.game = game
        self.socketio = socketio
        self.current_segment = -1
        self.segment_order = [
            SegmentType.CUPID,
            SegmentType.LOVERS,
            SegmentType.WEREWOLF,
            SegmentType.WITCH_HEAL,
            SegmentType.WITCH_KILL,
            SegmentType.SEER,
        ]

    def play_audio(self, filename):
        try:
            playsound(f"./assets/{filename}.mp3")
        except Exception as e:
            print(e)

    def start_night(self):
        self.current_segment = 0
        print("Starting night")
        # TODO: Uncomment this line to play the intro audio
        # self.play_audio("Intro")
        self.run_current_segment()

    def run_current_segment(self):
        segment = self.segment_order[self.current_segment]
        print("running segment", segment)
        if segment == SegmentType.CUPID:
            print("running cupid segment")
            self._run_cupid_segment()
        elif segment == SegmentType.WEREWOLF:
            self._run_werewolf_segment()
        elif segment == SegmentType.WITCH_HEAL:
            self._run_witch_heel_segment()
        elif segment == SegmentType.WITCH_KILL:
            self._run_witch_kill_segment()
        elif segment == SegmentType.SEER:
            self._run_seer_segment()

    def advance_segment(self):
        print("current segment is ", self.current_segment)
        if self.current_segment == 0:
            self.play_audio("Cupidon/Cupidon-2")
        if self.current_segment == 1:
            self.play_audio("Lovers/Lover-3")
        self.current_segment = (self.current_segment + 1) % len(self.segment_order)
        self.run_current_segment()

    def _run_cupid_segment(self):
        print("stating here")
        self.play_audio("Cupidon/Cupidon-1")
        cupid = self.game.get_player_by_role(PlayerRole.CUPID)
        self.socketio.emit(
            "cupidon_choice",
            {"message": "Choose two players to fall in love"},
            to=cupid.sid,
        )

    def _run_werewolf_segment(self):
        self.play_audio("Loup-garou-start")
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

    def _run_witch_heel_segment(self):
        if not self.game.witch_heal_available:
            return
        self.play_audio("Sorciere-1")
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
        print("Running witch kill segment")
        if not self.game.witch_kill_available:
            print("Witch kill not available")
            return
        self.play_audio("Sorciere-2")
        witch = self.game.get_player_by_role(PlayerRole.WITCH)
        print("witch kill available")
        if witch and witch.is_alive and self.game.witch_kill_available:
            try:
                self.socketio.emit(
                    "witch_kill",
                    {
                        "message": "Choose a player to kill",
                    },
                    to=witch.sid,
                )
            except Exception as e:
                print(e)

    def _run_seer_segment(self):
        self.play_audio("Seer-start")
        seer = self.game.get_player_by_role(PlayerRole.SEER)
        if seer:
            self.socketio.emit(
                "seer_choice",
                {"message": "Choose a player to investigate"},
                to=seer.sid,
            )

    def round_finished(self):
        for player in self.game.pending_deaths:
            player.is_alive = False

    def alert_lovers(self, player1, player2):
        self.play_audio("Lovers/Lover-1")
        self.socketio.emit("alert_lovers", {"lover": player2.name}, to=player1.sid)
        self.socketio.emit("alert_lovers", {"lover": player1.name}, to=player2.sid)

        self.play_audio("Lovers/Lover-2")

        self.socketio.emit("lover_can_close", to=player1.sid)
        self.socketio.emit("lover_can_close", to=player2.sid)
