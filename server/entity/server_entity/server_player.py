from functools import wraps

import errors
from config import CONFIG
from defs import Action, Result
from entity.game import Game, GameState
from entity.player import Player
from entity.serializable import Serializable
from logger import log

from entity.server_entity.server_role import ServerRole


def login_required(func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        if self.game is None or self._player is None:
            raise errors.AccessDenied('Login required')
        else:
            return func(self, *args, **kwargs)

    return wrapped


class ServerPlayer(ServerRole):
    def __init__(self):
        self._player = None
        self.game = None
        self.close_connection = False
        self.save_to_db = True
        super().__init__()

    @property
    def instance(self):
        return self._player

    def on_login(self, data: dict):
        if self.game is not None or self._player is not None:
            raise errors.BadCommand('You are already logged in')

        self.check_keys(data, ['name'])
        player_name = data['name']
        password = data.get('password', None)

        player = Player.get(player_name, password=password)
        if not player.check_password(password):
            raise errors.AccessDenied('Password mismatch')

        game_name = data.get('game', 'Game of {}'.format(player_name))
        num_players = data.get('num_players', CONFIG.DEFAULT_NUM_PLAYERS)
        num_turns = data.get('num_turns', CONFIG.DEFAULT_NUM_TURNS)
        num_observers = data.get('num_observers', CONFIG.DEFAULT_NUM_OBSERVERS)

        game = Game.get(game_name, num_players=num_players, num_turns=num_turns, num_observers=num_observers)

        game.check_state(GameState.INIT, GameState.RUN)
        player = game.add_player(player)

        self.game = game
        self._player = player
        self.close_connection = False

        log.info('Player successfully logged in: {}'.format(player), game=self.game)
        message = self._player.to_json_str()

        return Result.OKEY, message

    @login_required
    def on_logout(self, _):
        self.game.remove_player(self._player)
        log.info('Logout player: {}'.format(self._player.name), game=self.game)
        self.close_connection = True
        return Result.OKEY, None

    @login_required
    def on_get_map(self, data: dict):
        self.check_keys(data, ['layer'])
        message = self.game.get_map_layer(self._player, data['layer'])
        return Result.OKEY, message

    @login_required
    def on_move(self, data: dict):
        self.check_keys(data, ['train_idx', 'speed', 'line_idx'])
        self.game.check_state(GameState.RUN)
        with self._player.lock:
            self.game.move_train(self._player, data['train_idx'], data['speed'], data['line_idx'])
        return Result.OKEY, None

    @login_required
    def on_turn(self, _):
        self.game.check_state(GameState.RUN)
        self.game.turn(self._player)
        return Result.OKEY, None

    @login_required
    def on_upgrade(self, data: dict):
        self.check_keys(data, ['trains', 'posts'], aggregate_func=any)
        self.game.check_state(GameState.RUN)
        with self._player.lock:
            self.game.make_upgrade(
                self._player, posts_idx=data.get('posts', []), trains_idx=data.get('trains', [])
            )
        return Result.OKEY, None

    @login_required
    def on_player(self, _):
        message = self._player.to_json_str()
        return Result.OKEY, message

    def on_list_games(self, _):
        games = Serializable()
        games.set_attributes(
            games=Game.get_all_active_games_attributes()
        )
        return Result.OKEY, games.to_json_str()

    ACTION_MAP = {
        Action.LOGIN: on_login,
        Action.LOGOUT: on_logout,
        Action.MAP: on_get_map,
        Action.MOVE: on_move,
        Action.UPGRADE: on_upgrade,
        Action.TURN: on_turn,
        Action.PLAYER: on_player,
        Action.GAMES: on_list_games
    }
    LOGIN_ACTION = Action.LOGIN
