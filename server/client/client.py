import json
import socket

from client.abstract_client import AbstractClient
from config import CONFIG
from defs import Action
from defs import Result
from logger import get_logger


class Client(AbstractClient):
    MAP_LAYERS = {0, 1, 10}

    def __init__(self, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT, level='INFO'):
        self.server_address = address, port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger = get_logger(self.__class__.__name__, level=level, )
        self.idx = ''
        self.ACTION_DICT = {}

    def run_server(self):
        """ Starts the server
        """
        try:
            self.server.connect(self.server_address)
            shutdown = False
            while not shutdown:
                self.output_available_options()

                selected_action = None
                try:
                    selected_action = Action(int(input()))

                    method = self.ACTION_DICT[selected_action]
                    message = method()
                    converted_message = self.convert_message(selected_action, message)
                    self.send_message(converted_message)

                    result, message, data = self.receive_message()

                    if result == Result.OKEY:
                        self.logger.info('DONE! Received message: {}'.format(self.get_pretty_string(message)))
                    else:
                        self.logger.error('Error {}, message: {}'.format(result.name, self.get_pretty_string(message)))

                    if selected_action == Action.LOGIN:
                        self.idx = message.get('idx', self.idx)

                except ValueError as err:
                    self.logger.warning(err)
                except KeyError as err:
                    self.logger.warning('No functions for {} yet'.format(str(selected_action)))
                except KeyboardInterrupt as err:
                    shutdown = True
                    self.logger.info('End the code...')
        except json.decoder.JSONDecodeError as err:
            self.logger.error(err)

        except Exception as err:
            self.logger.error(err)
        finally:
            self.logger.info('Close the connection...')
            if self.logger.is_queued:
                self.logger.stop()
            self.server.close()

    def receive_message(self):
        """ Accepts a message from a connected server
        """
        data = self.receive_headers()

        return self.receive_data(data)

    def receive_data(self, data):
        result = Result(int.from_bytes(data[0:CONFIG.ACTION_HEADER], byteorder='little'))
        data = data[CONFIG.ACTION_HEADER:]
        message_len = int.from_bytes(data[0:CONFIG.MSGLEN_HEADER], byteorder='little')
        message = data[CONFIG.MSGLEN_HEADER:]
        while len(message) < message_len:
            message += self.server.recv(CONFIG.RECEIVE_CHUNK_SIZE)
        return result, json.loads(message.decode('utf-8') or '{}'), message[message_len:]

    def receive_headers(self):
        data = b''
        while len(data) < CONFIG.RESULT_HEADER + CONFIG.MSGLEN_HEADER:
            data += self.server.recv(CONFIG.RECEIVE_CHUNK_SIZE)
        return data

    def send_message(self, message: bytes) -> None:
        """ Sends a message to the connected server
        """
        self.server.sendto(message, self.server_address)

    def output_available_options(self):
        self.logger.info(
            '\n'.join(
                map(
                    lambda option: '{}. {}'.format(option.value, option.name),
                    self.ACTION_DICT.keys()
                )
            )
        )

    @staticmethod
    def convert_message(action, message=None):
        """ Converts the message to the desired format
        """
        converted_message = action.to_bytes(length=CONFIG.ACTION_HEADER, byteorder='little')
        if message is None:
            return converted_message + int.to_bytes(0, length=CONFIG.MSGLEN_HEADER,
                                                    byteorder='little')
        dump_message = json.dumps(message)
        return converted_message + len(
            dump_message
        ).to_bytes(length=CONFIG.MSGLEN_HEADER, byteorder='little') + dump_message.encode('utf-8')

    @staticmethod
    def get_pretty_string(message):
        """ Returns pretty performance of message
        """
        from pprint import pprint
        from io import StringIO
        f = StringIO()
        pprint(message, f)
        return f.getvalue()
