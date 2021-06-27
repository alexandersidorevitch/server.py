""" Server definitions.
"""
from enum import IntEnum


class Action(IntEnum):
    """ Only Client commands.
    """
    MOVE = 1
    UPGRADE = 2
    PLAYER = 3
    TURN = 4

    # Clients and Observers actions
    LOGIN = 101
    LOGOUT = 102
    GAMES = 107
    MAP = 110

    # Observer actions:
    OBSERVER_LOGIN = 200
    GAME = 201

    # This actions are not available for client:
    EVENT = 202


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
