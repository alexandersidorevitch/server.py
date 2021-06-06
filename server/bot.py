from pprint import pprint
from random import choice

from client import Client
from config import CONFIG
from defs import Action
from Graph import Graph


class Bot(Client):
    def __init__(self, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT):
        super().__init__(address, port)
        self.turns = list()
        self.selected_train_idx = 0
        self.map_layer = 0
        self.maps_start_points = {'map04': 10}

    def generate_moves(self) -> None:
        self.map_layer = 0
        message = self.on_get_map()
        converted_message = self.convert_message(Action.MAP, message)
        pprint(converted_message)
        self.send_message(converted_message)
        result, message, data = self.receive_message()
        g = Graph.Graph(result)
        self.turns = g.dijkstra(self.selected_train_idx, self.maps_start_points[result.get('name', 'map04')])

    def on_get_map(self) -> dict:
        if self.map_layer in {'0', '1', '10'}:
            return {'layer': self.map_layer}
        else:
            raise ValueError('No option for {} layer'.format(self.map_layer))

    def on_move(self) -> dict:
        print('Choose train_idx: ')
        train_idx = int(input())
        if not self.turns or self.selected_train_idx != train_idx:
            self.generate_moves()

        turn = self.turns.pop(0)
        return {'line_idx': turn.get('line_idx'), 'speed': turn.get('speed'), 'train_idx': train_idx}

    def on_login(self):
        name = choice(('Nazar', 'Oleg', 'Petr', 'Igor', 'Taras')) + 'Bot'
        print('Bot name: {}'.format(name))
        print('Input game name: ', end='')
        return {'name': name, 'game': input()}
