from multiprocessing import Lock, Process

import errors
from client.client import Client
from config import CONFIG
from defs import Action, Result


class Observer(Client):
    def __init__(self, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT, log_level='INFO'):
        super().__init__(address=address, port=port, level=log_level)
        self.receive_process = Process(target=self.receive_notification)
        self._receive_lock = Lock()
        self.shutdown = False
        self.ACTION_DICT = {
            Action.OBSERVER: self.on_observer,
            Action.GAME: self.on_game
        }

    def on_observer(self):
        return None

    def on_game(self):
        self.logger.info('Input game_idx:')
        return {'idx': int(input())}

    def run_server(self):
        try:
            self.server.connect(self.server_address)
            self.receive_process.start()
            self.shutdown = False

            while not self.shutdown:
                try:
                    selected_action = Action(int(input()))

                    with self._receive_lock:
                        if selected_action not in self.ACTION_DICT:
                            raise errors.ResourceNotFound(
                                'Functions for {} are not implemented yet'.format(str(selected_action)))

                        method = self.ACTION_DICT[selected_action]
                        message = method()
                        converted_message = self.convert_message(selected_action, message)
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
                self.logger.stop()

            self.server.close()

            if self.receive_process.is_alive():
                self.receive_process.terminate()

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
