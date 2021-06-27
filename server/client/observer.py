from threading import Lock, Thread

import errors
from client.client import Client
from config import CONFIG
from defs import Action, Result


class Observer(Client):
    def __init__(self, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT, log_level='INFO'):
        super().__init__(address=address, port=port, level=log_level)
        self.receive_process = Thread(target=self.receive_notification)
        self._receive_lock = Lock()
        self.shutdown = False
        self.ACTION_DICT = {
            Action.OBSERVER_LOGIN: self.on_login,
            Action.LOGOUT: self.on_logout,
            Action.MAP: self.on_get_map,
            Action.GAMES: self.on_list_games,
        }

    @staticmethod
    def on_get_map():
        return None

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
            self.receive_process.start()
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

            if self.receive_process.is_alive():
                self.receive_process.join(CONFIG.TURN_TIMEOUT)

    def receive_message(self):
        data = self.receive_headers()
        with self._receive_lock:
            return self.receive_data(data)

    def receive_notification(self):
        while not self.shutdown:
            self.output_available_options()
            try:
                result, message, data = self.receive_message()
            except OSError:
                self.shutdown = True
                break
            if result == Result.OKEY:
                self.logger.info('Done')
                self.logger.info('Received message: ')
                self.logger.info(self.get_pretty_string(message))
            else:
                self.logger.error('Error {}'.format(result))
