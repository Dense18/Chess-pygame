from enum import Enum, auto

class Status(Enum):
    ONGOING = auto()
    CHECK = auto()
    CHECKMATE = auto()
    STALEMATE = auto()
