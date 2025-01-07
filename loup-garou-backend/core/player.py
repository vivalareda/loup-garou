from dataclasses import dataclass
from typing import Optional

from .roles import PlayerRole


@dataclass
class Player:
    name: str
    sid: str
    role: Optional[PlayerRole] = None
    is_alive: bool = True
    lover_sid: Optional[str] = None

    def to_dict(self):
        return {
            "name": self.name,
            "sid": self.sid,
            "role": self.role.value if self.role else None,
            "is_alive": self.is_alive,
        }

    def __repr__(self):
        role_name = self.role if self.role else "No role assigned"
        return f"{self.name} is a {role_name}, current alive status: {self.is_alive}"
