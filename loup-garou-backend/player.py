class Player:
    def __init__(self, name, sid, role=None):
        self.name = name
        self.role = role
        self.sid = sid
        self.lover = None

    def __repr__(self):
        role_name = self.role if self.role else "No role assigned"
        return f"{self.name} - {role_name}"

    def assign_role(self, role):
        self.role = role
