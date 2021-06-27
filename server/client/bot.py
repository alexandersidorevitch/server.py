from random import choice

from client.client import Client
from config import CONFIG
from defs import Action
from entity.line import Line
from entity.train import Train
from graph import graph


class Bot(Client):
    def __init__(self, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT, log_level='INFO'):
        super().__init__(address=address, port=port, level=log_level)
        self.map_layer = 0
        self.train_paths = {}
        self.ACTION_DICT = {
            Action.MAP: self.on_get_map,
            Action.MOVE: self.on_move,
            Action.LOGOUT: self.on_logout,
            Action.LOGIN: self.on_login,
            Action.TURN: self.on_turn,
            Action.GAMES: self.on_game,
            Action.PLAYER: self.on_player,
        }

    @staticmethod
    def on_turn():
        return None

    @staticmethod
    def on_game():
        return None

    @staticmethod
    def on_player():
        return None

    @staticmethod
    def on_get_map():
        return None

    @staticmethod
    def on_logout():
        return None

    def on_get_map(self) -> dict:
        if self.map_layer not in self.MAP_LAYERS:
            raise ValueError('No option for {} layer'.format(self.map_layer))
        return {'layer': self.map_layer}

    def on_move(self) -> dict:
        self.logger.info('Input train_idx: ')
        train_idx = int(input())
        result, message, data = self.get_map(layer=1)
        train = Train(train_idx)
        train_kwargs = next(
            filter(lambda _train: _train.get('idx') == train_idx,
                   message.get('trains'))
        )
        if not train_kwargs:
            raise ValueError('No any train with idx {}'.format(train_idx))

        train.set_attributes(**train_kwargs)

        if self.idx != train.player_idx:
            raise ValueError('This is not your train!!!')

        result, message, data = self.get_map(layer=0)
        line = Line(train.line_idx)
        line_kwargs = next(
            filter(lambda _line: _line.get('idx') == train.line_idx,
                   message.get('lines'))
        )
        line.set_attributes(**line_kwargs)

        if train.speed != 0:
            raise ValueError('Train is moving')

        if train.idx not in self.train_paths:
            self.logger.info('Input end point_idx: ')
            end_point_idx = int(input())
            self.generate_moves(train.idx, line.points[train.position != 0], end_point_idx)

        move = self.train_paths[train.idx].pop(0)
        if not self.train_paths[train.idx]:
            del self.train_paths[train.idx]

        return {'line_idx': move.get('line_idx'), 'speed': move.get('speed'), 'train_idx': train_idx}

    def on_login(self):
        name = choice(('Nazar', 'Oleg', 'Petr', 'Igor', 'Taras')) + 'Bot'
        self.logger.info('Bot name: {}'.format(name))
        self.logger.info('Input game name: ')
        return {'name': name, 'game': input()}

    def get_map(self, layer):
        """ Returns the selected map
        """
        self.map_layer = layer
        message = self.on_get_map()
        converted_message = self.convert_message(Action.MAP, message)
        self.send_message(converted_message)
        return self.receive_message()

    def generate_moves(self, train_idx, start_point_idx, end_point_idx) -> None:
        """ Generates moves for the selected train
        """
        result, message, data = self.get_map(0)

        g = graph.Graph(message)
        self.train_paths[train_idx] = g.dijkstra(start_point_idx, end_point_idx).get('path')
