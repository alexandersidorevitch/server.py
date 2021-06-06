import json

from client import Client
from config import CONFIG
from defs import Action, Result


class Player(Client):
    def __init__(self, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT):
        super().__init__(address, port)
        super().ACTION_DICT[Action.MAP] = Player.on_get_map
        super().ACTION_DICT[Action.MOVE] = Player.on_move
        super().ACTION_DICT[Action.LOGIN] = Player.on_login

    def on_get_map(self):
        print('Layer 0 - static objects: ‘idx’, ‘name’, ‘points’, ‘lines’',
              'Layer 1 - dynamic objects: ‘idx’, ‘posts’, ‘trains’, ‘ratings’',
              'Layer 10 - coordinates of points: ‘idx’, ‘size’, ‘coordinates’', sep='\n')
        print('Select layer: ')
        layer = input()
        if layer in ['0', '1', '10']:
            return {'layer': int(layer)}
        else:
            raise ValueError('No option for {} layer'.format(layer))

    def on_move(self):
        print('Choose line idx: ')
        line_idx = int(input())
        direction = {'pos': 1, 'neg': -1, 'stop': 0}
        print('Choose direction (enable options {})'.format(list(direction)))
        speed = direction[input()]
        print('Choose train_idx: ')
        train_idx = int(input())
        return {'line_idx': line_idx, 'speed': speed, 'train_idx': train_idx}

    def on_login(self):
        print('Write your name: ', end='')
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
            print('{} - {}'.format(option, description))
            print('Press enter for default value...')
            print(option.capitalize())
            value = input()
            if value:
                message[option] = int(value) if option.startswith('num') else value

        return message


def main():
    # server_address = CONFIG.SERVER_ADDR, CONFIG.SERVER_PORT
    player = Player()
    try:
        player.run_server()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    print('Starting server...')
    main()
    print('End server...')
