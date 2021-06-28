from threading import Lock, Thread

import errors
from client.client import Client
from config import CONFIG
from defs import Action, Result


class Observer(Client):
    def __init__(self, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT, log_level='INFO'):
        super().__init__(address=address, port=port, level=log_level)
        self.receive_thread = Thread(target=self.receive_notification)
        self._receive_lock = Lock()
        self.shutdown = False
        self.ACTION_DICT = {
            Action.OBSERVER_LOGIN: self.on_login,
            Action.LOGOUT: self.on_logout,
            Action.MAP: self.on_get_map,
            Action.GAMES: self.on_list_games,
        }

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

    @staticmethod
    def on_list_games():
        return None

    @staticmethod
    def on_logout():
        return None

    def on_login(self):
        self.logger.info('Write your name: ')
        message = {'name': input()}

        not_required_options = (
            ('game', 'game’s name (use it to connect to existing game)'),
            ('num_turns', 'number of game turns to be played, default:'
                          ' -1 (if num_turns < 1 it means that the game is unlimited)'),
            ('num_players', 'number of players in the game, default: 1'),
            ('num_observers', 'number of observers in the game, default: 0'),
        )

        for option, description in not_required_options:
            self.logger.info('{} - {}\n'
                             'Press enter for default value...\n'
                             '{}'.format(option, description, option.capitalize()))

            value = input()
            if value:
                message[option] = int(value) if option.startswith('num') else value
        return message

    def run_server(self):
        try:
            self.server.connect(self.server_address)
            self.receive_thread.start()
            self.shutdown = False

            while not self.shutdown:
                try:
                    selected_action = Action(int(input()))

                    if selected_action not in self.ACTION_DICT:
                        raise errors.ResourceNotFound(
                            'Functions for {} are not implemented yet'.format(str(selected_action)))

                    method = self.ACTION_DICT[selected_action]
                    message = method()
                    converted_message = self.convert_message(selected_action, message)
                    with self._receive_lock:
                        self.send_message(converted_message)

                except ValueError as err:
                    self.logger.warning(err)
                except errors.ResourceNotFound as err:
                    self.logger.warning(err)
                except KeyboardInterrupt as err:
                    self.shutdown = True
                    self.logger.info('End the code...')

        except Exception as err:
            self.logger.error(err)
        finally:
            self.logger.info('Close the connection...')

            if self.logger.is_queued:
                self.logger.info('Close the logger...')
                self.logger.stop()

            self.logger.info('Close the server...')
            self.server.close()
            self.logger.info('Close the thread...')

            if self.receive_thread.is_alive():
                self.receive_thread.join(CONFIG.TURN_TIMEOUT)

    def receive_message(self):
        data = self.receive_headers()
        with self._receive_lock:
            return self.receive_data(data)

    def receive_notification(self):
        while not self.shutdown:
            self.output_available_options()
            try:
                result, message, data = self.receive_message()
                if result == Result.OKEY:
                    self.logger.info('DONE! Received message: {}'.format(self.get_pretty_string(message)))
                else:
                    self.logger.error('Error {}, message: {}'.format(result.name, self.get_pretty_string(message)))
            except OSError:
                self.shutdown = True
                break
