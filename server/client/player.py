import json

from client import Client
from config import CONFIG
from defs import Action, Result


class Player(Client):
    def __init__(self, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT, log_level='INFO'):
        super().__init__(address=address, port=port, level=log_level)
        self.ACTION_DICT = {
            Action.MAP: self.on_get_map,
            Action.MOVE: self.on_move,
            Action.LOGOUT: self.on_logout,
            Action.LOGIN: self.on_login,
            Action.TURN: self.on_turn,
            Action.GAMES: self.on_game,
            Action.PLAYER: self.on_player,
        }

    def on_turn(self):
        return None

    def on_game(self):
        return None

    def on_player(self):
        return None

    def on_get_map(self):
        return None

    def on_logout(self):
        return None

    def on_get_map(self):
        self.logger.info(
            'Layer 0 - static objects: ‘idx’, ‘name’, ‘points’, ‘lines’\n'
            'Layer 1 - dynamic objects: ‘idx’, ‘posts’, ‘trains’, ‘ratings’\n'
            'Layer 10 - coordinates of points: ‘idx’, ‘size’, ‘coordinates’\n')
        self.logger.info('Select layer: ')
        layer = int(input())
        if layer not in self.MAP_LAYERS:
            raise ValueError('No option for {} layer'.format(layer))
        return {'layer': layer}

    def on_move(self):
        self.logger.info('Choose line idx: ')
        line_idx = int(input())

        direction = {'pos': 1, 'neg': -1, 'stop': 0}
        self.logger.info('Choose direction (enable options {})'.format(list(direction)))
        speed = direction[input()]

        self.logger.info('Choose train_idx: ')
        train_idx = int(input())
        return {'line_idx': line_idx, 'speed': speed, 'train_idx': train_idx}

    def on_login(self):
        self.logger.info('Write your name: ')
        message = {'name': input()}

        not_required_options = (
            ('password', 'player’s password used to verify the connection,'
                         ' if player with the same name tries to connect with another password - login will be rejected'),
            ('game', 'game’s name (use it to connect to existing game)'),
            ('num_turns', 'number of game turns to be played, default:'
                          ' -1 (if num_turns < 1 it means that the game is unlimited)'),
            ('num_players', 'number of players in the game, default: 1')
        )

        for option, description in not_required_options:
            self.logger.info('{} - {}\n'
                             'Press enter for default value...\n'
                             '{}'.format(option, description, option.capitalize()))

            value = input()
            if value:
                message[option] = int(value) if option.startswith('num') else value

        return message
