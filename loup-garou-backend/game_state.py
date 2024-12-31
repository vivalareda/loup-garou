from playsound import playsound


class GameState:

    def __init__(self, socketio):
        self.phase = "waiting"
        self.socketio = socketio
        self.round = 0
        self.players_alive = set()
        self.votes = {}
        self.night_actions = {}

        self.hunter_sid = None
        self.hunter_choice = None

        self.cupidon_sid = None
        self.cupidon_choice = None

        self.seer_sid = None

    def start_game(self, players):
        self.players = players
        self.players_alive = set(players.keys())
        self.phase = "night"
        self.round = 1
        self.narrate_intro()
        self.cupidon_segment()

    def narrate_intro(self):
        playsound("./assets/Intro.mp3")

    def process_night_action(self, player_id, action, target_id):
        self.night_actions[player_id] = {"action": action, "target": target_id}

    def process_vote(self, voter_id, target_id):
        if voter_id in self.players_alive:
            self.votes[voter_id] = target_id

    def cupidon_segment(self):
        playsound("./assets/Cupidon.mp3")
        print(self.cupidon_sid)
        self.socketio.emit(
            "cupidon_choice",
            {"message": "It's your turn, Cupidon!"},
            to=self.cupidon_sid,
        )

    def hunter_segment(self):
        playsound("./assets/Hunter-start.mp3")
        self.socketio.emit(
            "hunter_choice",
            {"message": "It's your turn, Hunter!"},
            to=self.hunter_sid,
        )

    def count_votes(self):
        if not self.votes:
            return None
        vote_counts = {}
        for target in self.votes.values():
            vote_counts[target] = vote_counts.get(target, 0) + 1
        return max(vote_counts.items(), key=lambda x: x[1])[0]

    def setCupidonSid(self, sid):
        self.cupidon_sid = sid

    def setHunterSid(self, sid):
        self.hunter_sid = sid

    def setCupidonChoice(self, sids):
        for player in self.players.values():
            if player.sid == sids[0]:
                player.lover = sids[1]
            elif player.sid == sids[1]:
                player.lover = sids[0]

    def setHunterChoice(self, sid):
        self.hunter_choice = sid

    def seer_segment(self):
        playsound("./assets/Seer-start.mp3")
        self.socketio.emit(
            "seer_choice",
            {"message": "It's your turn, Seer!"},
            to=self.seer_sid,
        )

    def setSeerSid(self, sid):
        self.seer_sid = sid
