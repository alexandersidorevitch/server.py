from pprint import pprint
from random import choice

from client import Client
from config import CONFIG
from defs import Action
from graph import graph
from entity.train import Train
from entity.line import Line


class Bot(Client):
    def __init__(self, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT):
        super().__init__(address, port)
        self.map_layer = 0
        self.train_paths = dict()

    def generate_moves(self, train_idx, start_point_idx, end_point_idx) -> None:

        result, message, data = self.get_map(0)

        g = graph.Graph(message)
        self.train_paths[train_idx] = g.dijkstra(start_point_idx, end_point_idx).get('path')

    def on_get_map(self) -> dict:
        if self.map_layer not in self.MAP_LAYERS:
            raise ValueError('No option for {} layer'.format(self.map_layer))
        return {'layer': self.map_layer}

    def on_move(self) -> dict:
        Client.output('Input train_idx: ', CONFIG.DEFAULT_OUTPUT_FUNCTION)
        train_idx = int(input())
        print('1')
        result, message, data = self.get_map(layer=1)
        train = Train(train_idx)
        train_kwargs = next(
            filter(lambda _train: _train.get('idx') == train_idx,
                   message.get('trains'))
        )
        if not train_kwargs:
            raise ValueError('No any train with idx {}'.format(train_idx))

        print('2')
        train.set_attributes(**train_kwargs)

        if self.idx != train.player_idx:
            raise ValueError('This is not your train!!!')

        print('3')
        result, message, data = self.get_map(layer=0)
        print('6')
        line = Line(train.line_idx)
        print(line)
        print('7')
        print(self.get_map(layer=0))
        line_kwargs = next(
            filter(lambda _line: _line.get('idx') == train.line_idx,
                   message.get('lines'))
        )
        print('4')
        line.set_attributes(**line_kwargs)

        if train.speed != 0:
            raise ValueError('Train is moving')

        if train.idx not in self.train_paths:
            print('5')
            Client.output('Input end point_idx: ', CONFIG.DEFAULT_OUTPUT_FUNCTION, end='')
            end_point_idx = int(input())
            self.generate_moves(train.idx, line.points[train.position != 0], end_point_idx)

        turn = self.train_paths[train.idx].pop(0)
        if not self.train_paths[train.idx]:
            del self.train_paths[train.idx]

        return {'line_idx': turn.get('line_idx'), 'speed': turn.get('speed'), 'train_idx': train_idx}

    def on_login(self):
        name = choice(('Nazar', 'Oleg', 'Petr', 'Igor', 'Taras')) + 'Bot'
        Client.output('Bot name: {}'.format(name), CONFIG.DEFAULT_OUTPUT_FUNCTION)
        Client.output('Input game name: ', CONFIG.DEFAULT_OUTPUT_FUNCTION, end='')
        return {'name': name, 'game': input()}

    def get_map(self, layer):
        self.map_layer = layer
        message = self.on_get_map()
        converted_message = self.convert_message(Action.MAP, message)
        self.send_message(converted_message)
        return self.receive_message()
