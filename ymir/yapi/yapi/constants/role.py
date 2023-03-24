from dataclasses import dataclass
from functools import total_ordering
from typing import Any


@total_ordering
@dataclass
class Role:
    name: str
    description: str
    rank: int

    def __eq__(self, other: Any) -> bool:
        return self.rank == other.rank

    def __lt__(self, other: Any) -> bool:
        return self.rank < other.rank


class Roles:
    NORMAL = Role("NORMAL", "Normal User", 1)
    ADMIN = Role("ADMIN", "Admin User, managing Normal User", 2)
    SUPER_ADMIN = Role("SUPER_ADMIN", "Super Admin User, managing Admin User", 3)
