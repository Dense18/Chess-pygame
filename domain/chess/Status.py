from enum import Enum, auto

class Status(Enum):
    """
        Enum about the current chess game status
    """
    ONGOING = auto()
    CHECK = auto()
    CHECKMATE = auto()
    STALEMATE = auto()
