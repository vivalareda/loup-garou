class Game:
    def __init__(self):
        self.game_state = GameState()
        self.players = {}
        self.pending_deaths = []
        self.night_actions = {}

    def add_player(self, name, sid):
        player = Player(name, sid)
        self.players[sid] = player
        return player

    def get_player_by_role(self, role):
        return next((p for p in self.players.values() if p.role == role), None)

    def get_players_by_role(self, role):
        return [p for p in self.players.values() if p.role == role]

    def add_pending_death(self, player):
        self.pending_deaths.append(player)

    def get_last_pending_death(self):
        return self.pending_deaths[-1] if self.pending_deaths else None
