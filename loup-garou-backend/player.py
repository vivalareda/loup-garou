class Player:
    players = []  # Class variable to store all players

    def __init__(self, name, sid, role=None):
        self.name = name
        self.role = role
        self.sid = sid
        self.lover = None
        Player.players.append(self)  # Add the new player to the list

    def __repr__(self):
        role_name = self.role if self.role else "No role assigned"
        return f"{self.name} - {role_name}"

    def assign_role(self, role):
        self.role = role

    @classmethod
    def get_all_players(cls):
        return cls.players

    @classmethod
    def getPlayerByName(cls, name):
        for player in cls.players:
            if player.name == name:
                return player
        return None  # Return None if no player with the given name is found

    @classmethod
    def getPlayerBySid(cls, sid):
        print(cls.players)
        for player in cls.players:
            if player.sid == sid:
                return player
        return None  # Return None if no player with the given sid is found
