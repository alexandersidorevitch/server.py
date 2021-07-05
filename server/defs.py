""" Server definitions.
"""
from enum import IntEnum, auto


class Action(IntEnum):
    """ Only Client commands.
    """
    LOGIN = auto()
    MOVE = auto()
    UPGRADE = auto()
    PLAYER = auto()
    TURN = auto()

    # Clients and Observers actions
    LOGOUT = auto()
    GAMES = auto()
    MAP = auto()

    # Observer actions:
    OBSERVER_LOGIN = auto()
    GAME = auto()

    # This actions are not available for client:
    EVENT = auto()


class Result(IntEnum):
    """ Server response codes.
    """
    OKEY = 0
    BAD_COMMAND = 1
    RESOURCE_NOT_FOUND = 2
    ACCESS_DENIED = 3
    INAPPROPRIATE_GAME_STATE = 4
    TIMEOUT = 5
    INTERNAL_SERVER_ERROR = 500
