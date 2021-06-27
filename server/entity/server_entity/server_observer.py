""" Observer Entity. Handles requests when client connects to server as OBSERVER to watch replay(s).
"""

import errors
from config import CONFIG
from defs import Action, Result
from entity.game import Game, GameState
from entity.observer import Observer
from entity.serializable import Serializable
from logger import log

from entity.server_entity.server_role import ServerRole


def game_required(func):
    def wrapped(self, *args, **kwargs):
        if self.game is None:
            raise errors.BadCommand('A game is not chosen')
        else:
            return func(self, *args, **kwargs)

    return wrapped


class ServerObserver(ServerRole):

    def __init__(self):
        self._observer = None
        self.game = None
        self.close_connection = False
        self.save_to_db = False
        super().__init__()

    @property
    def instance(self):
        return self._observer

    def on_login(self, data):
        """ Returns list of games.
        """
        if self.game is not None or self._observer is not None:
            raise errors.BadCommand('You are already logged in')

        self.check_keys(data, ['name'])
        observer_name = data['name']
        observer = Observer(observer_name)

        game_name = data.get('game', 'Game of {}'.format(observer_name))
        num_players = data.get('num_players', CONFIG.DEFAULT_NUM_PLAYERS)
        num_turns = data.get('num_turns', CONFIG.DEFAULT_NUM_TURNS)
        num_observers = data.get('num_observers', CONFIG.DEFAULT_NUM_OBSERVERS)

        game = Game.get(game_name, num_players=num_players, num_turns=num_turns, num_observers=num_observers)

        game.check_state(GameState.INIT, GameState.RUN)
        observer = game.add_observer(observer)
        self._observer = observer
        self.game = game

        log.info('Observer successfully logged in: {!r}'.format(observer), game=self.game)
        message = self._observer.to_json_str()

        return Result.OKEY, message

    @game_required
    def on_logout(self, _):
        log.info('Logout observer', game=self.game)
        self.game.remove_observer(self._observer)
        self.close_connection = True
        return Result.OKEY, None

    @game_required
    def on_get_map(self, data):
        """ Returns specified game map layer.
        """
        self.check_keys(data, ['layer'])
        message = self.game.get_map_layer(None, data['layer'])
        return Result.OKEY, message

    def on_list_games(self, _):
        games = Serializable()
        games.set_attributes(
            games=Game.get_all_active_games_attributes()
        )
        return Result.OKEY, games.to_json_str()

    ACTION_MAP = {
        Action.OBSERVER_LOGIN: on_login,
        Action.LOGOUT: on_logout,
        Action.MAP: on_get_map,
        Action.GAMES: on_list_games
    }
    LOGIN_ACTION = Action.OBSERVER_LOGIN
