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
    DAY = "day"


class SegmentManager:
    def __init__(self, game, socketio):
        self.first_night = True
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
            SegmentType.DAY,
        ]

    def play_audio(self, filename):
        try:
            playsound(f"./assets/{filename}.mp3")
        except Exception as e:
            print(e)

    def play_start_audio(self, segment):
        if segment == SegmentType.CUPID:
            self.play_audio("Cupidon/Cupidon-1")
        if segment == SegmentType.LOVERS:
            self.play_audio("Lovers/Lover-1")
        elif segment == SegmentType.WEREWOLF:
            self.play_audio("Werewolves/Werewolves-1")
        elif segment == SegmentType.WITCH_HEAL:
            self.play_audio("Sorciere-1")
        elif segment == SegmentType.WITCH_KILL:
            self.play_audio("Sorciere-2")

    def start_night(self):
        self.current_segment = 0
        print("Starting night")
        # TODO: Uncomment this line to play the intro audio
        self.play_audio("Intro")
        self.run_current_segment()

    def run_current_segment(self):
        segment = self.segment_order[self.current_segment]
        print("running segment", segment)
        if segment == SegmentType.CUPID:
            if not self.first_night:
                self.advance_segment()
            # print("running cupid segment")
            self._run_cupid_segment()
            # self.advance_segment()  # TODO remove this when want cupid to run
        elif segment == SegmentType.LOVERS:
            self._run_lovers_segment()
            # self.advance_segment()  # TODO remove this when want cupid to run
        elif segment == SegmentType.WEREWOLF:
            print("running_werewolf")
            self._run_werewolf_segment()
        elif segment == SegmentType.WITCH_HEAL:
            self.advance_segment()  # TODO remove this when want cupid to run
            # self._run_witch_heal_segment()
        elif segment == SegmentType.WITCH_KILL:
            # self.advance_segment()  # TODO remove this when want cupid to run
            self._run_witch_kill_segment()
        elif segment == SegmentType.SEER:
            self.advance_segment()
            # self._run_seer_segment()
        elif segment == SegmentType.DAY:
            self.night_finished()

    def advance_segment(self):
        print("current segment is ", self.current_segment)
        if self.current_segment == 0 and self.first_night:
            self.play_audio("Cupidon/Cupidon-2")
        if self.current_segment == 1 and self.first_night:
            self.play_audio("Lovers/Lover-3")
        if self.current_segment == 2:
            self.play_audio("Werewolves/Werewolves-2")
            print("played werewolves")
        if self.current_segment == 4:
            self.play_audio("Sorciere-3")
        if self.current_segment == 5:
            self.play_audio("Wake-up-everyone")
        self.current_segment = (self.current_segment + 1) % len(self.segment_order)
        self.run_current_segment()

    def _run_cupid_segment(self):
        print("stating here")
        self.play_start_audio(SegmentType.CUPID)
        # TODO : uncomment this and remove the hard coded value this is how to get cupid player
        # cupid = self.game.get_player_by_role(PlayerRole.CUPID)
        print("cupid sid", self.game.cupid)

        self.socketio.emit(
            "cupidon_choice",
            {"message": "Choose two players to fall in love"},
            to=self.game.cupid,
            # CHANGE to cupid.sid
        )

    def _run_werewolf_segment(self):
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
        if not self.game.witch_kill_available:
            return
        self.play_start_audio(SegmentType.WITCH_KILL)
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
        self.play_start_audio(SegmentType.SEER)
        seer = self.game.get_player_by_role(PlayerRole.SEER)
        if seer:
            self.socketio.emit(
                "seer_choice",
                {"message": "Choose a player to investigate"},
                to=seer.sid,
            )

    def night_finished(self):
        print("Pending death ", len(self.game.pending_deaths))
        self.first_night = False
        if len(self.game.pending_deaths) == 0:
            self.play_audio("Night-end/No-deaths")
        else:
            self.play_audio("Night-end/Deaths")
            print(self.game.pending_deaths)
            for sid in self.game.pending_deaths:
                player = self.game.get_player(sid)
                player.is_alive = False
                self.alert_dead_player(player)

        self.start_day_vote()

    def start_day_vote(self):
        self.socketio.sleep(1)
        print("Starting day vote")
        self.socketio.emit("day_vote")

    def count_votes(self):
        top_player = self.game.get_top_voted_player()
        if len(top_player) == 1:
            player = self.game.get_player(top_player[0])
            if player.lover_sid:
                self.alert_dead_player(player.lover_sid)
            self.alert_dead_player(top_player[0])

    def _run_lovers_segment(self):
        self.play_start_audio(SegmentType.LOVERS)
        lovers = self.game.get_lovers()
        player1, player2 = lovers
        self.socketio.emit("alert_lovers", {"lover": player2.name}, to=player1.sid)
        self.socketio.emit("alert_lovers", {"lover": player1.name}, to=player2.sid)

        self.play_audio("Lovers/Lover-2")

        self.socketio.emit("lover_can_close", to=player1.sid)
        self.socketio.emit("lover_can_close", to=player2.sid)

    def alert_dead_player(self, player):
        print("Alerting dead player", player.sid)
        try:
            self.socketio.emit("alert_dead", to=player.sid)
        except Exception as e:
            print(e)

    def reset_current_segment(self):
        current_segment = -1
