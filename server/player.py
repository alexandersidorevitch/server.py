import json

from client import Client
from config import CONFIG
from defs import Action, Result


class Player(Client):
    def __init__(self, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT):
        super().__init__(address, port)

    def on_get_map(self):
        Client.output('Layer 0 - static objects: ‘idx’, ‘name’, ‘points’, ‘lines’\n' +
                      'Layer 1 - dynamic objects: ‘idx’, ‘posts’, ‘trains’, ‘ratings’\n' +
                      'Layer 10 - coordinates of points: ‘idx’, ‘size’, ‘coordinates’\n',
                      CONFIG.DEFAULT_OUTPUT_FUNCTION)
        Client.output('Select layer: ', CONFIG.DEFAULT_OUTPUT_FUNCTION, end='')
        layer = int(input())
        if layer not in self.MAP_LAYERS:
            raise ValueError('No option for {} layer'.format(layer))
        return {'layer': int(layer)}

    def on_move(self):
        Client.output('Choose line idx: ', CONFIG.DEFAULT_OUTPUT_FUNCTION)
        line_idx = int(input())

        direction = {'pos': 1, 'neg': -1, 'stop': 0}
        Client.output('Choose direction (enable options {})'.format(list(direction)), CONFIG.DEFAULT_OUTPUT_FUNCTION)
        speed = direction[input()]

        Client.output('Choose train_idx: ', CONFIG.DEFAULT_OUTPUT_FUNCTION)
        train_idx = int(input())
        return {'line_idx': line_idx, 'speed': speed, 'train_idx': train_idx}

    def on_login(self):
        Client.output('Write your name: ', CONFIG.DEFAULT_OUTPUT_FUNCTION, end='')
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
            Client.output('{} - {}'.format(option, description), CONFIG.DEFAULT_OUTPUT_FUNCTION)
            Client.output('Press enter for default value...', CONFIG.DEFAULT_OUTPUT_FUNCTION)
            Client.output(option.capitalize(), CONFIG.DEFAULT_OUTPUT_FUNCTION)
            value = input()
            if value:
                message[option] = int(value) if option.startswith('num') else value

        return message


def main():
    player = Player()
    try:
        player.run_server()
    except Exception as e:
        CONFIG.DEFAULT_OUTPUT_FUNCTION(e)


if __name__ == '__main__':
    CONFIG.DEFAULT_OUTPUT_FUNCTION('Starting server...')
    main()
    CONFIG.DEFAULT_OUTPUT_FUNCTION('End server...')
