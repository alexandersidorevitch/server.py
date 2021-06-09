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
        super().ACTION_DICT[Action.MAP] = Bot.on_get_map
        super().ACTION_DICT[Action.MOVE] = Bot.on_move
        super().ACTION_DICT[Action.LOGIN] = Bot.on_login
        self.turns = list()
        self.selected_train_idx = 0
        self.map_layer = 0
        self.maps_end_points = {'map04': 10}
        self.current_train_point_idx = 0

    def generate_moves(self) -> None:
        self.map_layer = 0

        message = self.on_player()
        converted_message = self.convert_message(Action.PLAYER, message)
        self.send_message(converted_message)
        result, message, data = self.receive_message()
        start_train_point_idx = message.get('home').get('idx')

        result, message, data = self.get_map(0)

        g = graph.Graph(result)
        self.turns = g.dijkstra(start_train_point_idx, self.maps_end_points[message.get('name', 'map04')]).get('path')

    def on_get_map(self) -> dict:
        if self.map_layer in self.MAP_LAYERS:
            return {'layer': self.map_layer}
        else:
            raise ValueError('No option for {} layer'.format(self.map_layer))

    def on_move(self) -> dict:
        Client.output('Choose train_idx: ', CONFIG.DEFAULT_OUTPUT_FUNCTION)
        train_idx = int(input())

        result, message, data = self.get_map(layer=1)
        train = Train(train_idx)
        train_kwargs = next(
            filter(lambda train: train.get('idx') == train_idx,
                   message.get('trains', []))
        )
        train.set_attributes(**train_kwargs)

        result, message, data = self.get_map(layer=0)
        line = Line(train.line_idx)
        line_kwargs = next(
            filter(lambda line: line.get('idx') == train.line_idx,
                   message.get('lines', []))
        )
        line.set_attributes(**line_kwargs)

        if not self.turns or self.selected_train_idx != train_idx:
            self.generate_moves()

        if train.position == line.length:
            self.turns.remove(0)
            return {'line_idx': line.idx, 'speed': 0, 'train_idx': train_idx}

        turn = self.turns[0]
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
