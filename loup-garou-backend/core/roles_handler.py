class DeathManager(self):
    def __init__(self):
        self.pending_deaths = []
        self.veto_player = None
        self.player_votes_count = {}
        self.werewolves_alive = 0
        self.villagers_alive = 0
        self.players = []
