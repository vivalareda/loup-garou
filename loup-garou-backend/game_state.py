class GameState:

    def __init__(self, socketio):
        self.phase = "waiting"
        self.socketio = socketio
        self.round = 0
        self.players_alive = set()
        self.votes = {}
        self.night_actions = {}
        self.cupidon_sid = None
        self.cupidon_choice = None

    def start_game(self, players):
        self.players_alive = set(players.keys())
        self.phase = "night"
        self.round = 1
        self.handle_night()

    def process_night_action(self, player_id, action, target_id):
        self.night_actions[player_id] = {"action": action, "target": target_id}

    def process_vote(self, voter_id, target_id):
        if voter_id in self.players_alive:
            self.votes[voter_id] = target_id

    def handle_night(self):
        if self.round == 1:
            print("Cupidon's turn, SID:", self.cupidon_sid)
            self.socketio.emit(
                "cupidon_choice",
                {"message": "It's your turn, Cupidon!"},
                to=self.cupidon_sid,
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
