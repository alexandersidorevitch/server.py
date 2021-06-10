import json

import socket, threading, time

from config import CONFIG
from defs import Result, Action


class Client:
    MAP_LAYERS = {0, 1, 10}

    def __init__(self, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT):
        self.server_address = address, port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ACTION_DICT = {
            Action.MAP: self.on_get_map,
            Action.MOVE: self.on_move,
            Action.LOGOUT: self.on_logout,
            Action.LOGIN: self.on_login,
            Action.TURN: self.on_turn,
            Action.GAMES: self.on_game,
            Action.PLAYER: self.on_player,
        }

    def on_turn(self):
        return None

    def on_game(self):
        return None

    def on_player(self):
        return None

    def on_logout(self):
        return None

    def on_get_map(self):
        # To override
        raise NotImplementedError('Needs to redefine the method in the child class')

    def on_move(self):
        # To override
        raise NotImplementedError('Needs to redefine the method in the child class')

    def on_login(self):
        # To override
        raise NotImplementedError('Needs to redefine the method in the child class')

    def run_server(self):
        try:
            self.server.connect(self.server_address)
            shutdown = False
            while not shutdown:
                Client.output('{}. Action.LOGIN'.format(Action.LOGIN), CONFIG.DEFAULT_OUTPUT_FUNCTION)
                Client.output('{}. Action.LOGOUT'.format(Action.LOGOUT), CONFIG.DEFAULT_OUTPUT_FUNCTION)
                Client.output('{}. Action.MOVE'.format(Action.MOVE), CONFIG.DEFAULT_OUTPUT_FUNCTION)
                Client.output('{}. Action.TURN'.format(Action.TURN), CONFIG.DEFAULT_OUTPUT_FUNCTION)
                Client.output('{}. Action.PLAYER'.format(Action.PLAYER), CONFIG.DEFAULT_OUTPUT_FUNCTION)
                Client.output('{}. Action.GAMES'.format(Action.GAMES), CONFIG.DEFAULT_OUTPUT_FUNCTION)
                Client.output('{}. Action.MAP'.format(Action.MAP), CONFIG.DEFAULT_OUTPUT_FUNCTION)

                selected_action = None
                try:
                    selected_action = Action(int(input()))

                    method = self.ACTION_DICT[selected_action]
                    message = method()
                    converted_message = self.convert_message(selected_action, message)
                    Client.output(converted_message, CONFIG.DEFAULT_OUTPUT_FUNCTION)
                    self.send_message(converted_message)

                    result, message, data = self.receive_message()

                    if result == Result.OKEY:
                        Client.output('Done', CONFIG.DEFAULT_OUTPUT_FUNCTION)
                    else:
                        Client.output('Error {}'.format(result), CONFIG.DEFAULT_OUTPUT_FUNCTION)

                    Client.output('Received message: ', CONFIG.DEFAULT_OUTPUT_FUNCTION)
                    Client.output(message, CONFIG.DEFAULT_OUTPUT_FUNCTION)
                except ValueError as err:
                    Client.output(err, CONFIG.DEFAULT_OUTPUT_FUNCTION)
                except KeyError as err:
                    Client.output('No functions for {} yet'.format(selected_action), CONFIG.DEFAULT_OUTPUT_FUNCTION)
                except KeyboardInterrupt as err:
                    shutdown = True
                    Client.output('End the code...', CONFIG.DEFAULT_OUTPUT_FUNCTION)
        except json.decoder.JSONDecodeError as err:
            Client.output(err, CONFIG.DEFAULT_OUTPUT_FUNCTION)

        except Exception as err:
            Client.output(err, CONFIG.DEFAULT_OUTPUT_FUNCTION)
        finally:
            Client.output('Close the connection...', CONFIG.DEFAULT_OUTPUT_FUNCTION)
            self.server.close()

    def receive_message(self):
        data = self.server.recv(CONFIG.RECEIVE_CHUNK_SIZE)
        result = Result(int.from_bytes(data[0:CONFIG.ACTION_HEADER], byteorder='little'))

        data = data[CONFIG.ACTION_HEADER:]
        message_len = int.from_bytes(data[0:CONFIG.MSGLEN_HEADER], byteorder='little')

        message = data[CONFIG.MSGLEN_HEADER:]
        while len(message) < message_len:
            message += self.server.recv(CONFIG.RECEIVE_CHUNK_SIZE)
        return result, json.loads(message.decode('utf-8') or '{}'), message[message_len:]

    @staticmethod
    def convert_message(action, message=None):
        converted_message = action.to_bytes(length=CONFIG.ACTION_HEADER, byteorder='little')
        if message is None:
            return converted_message + int.to_bytes(0, length=CONFIG.MSGLEN_HEADER,
                                                    byteorder='little')
        dump_message = json.dumps(message)
        return converted_message + len(
            dump_message).to_bytes(length=CONFIG.MSGLEN_HEADER,
                                   byteorder='little') + dump_message.encode(
            'utf-8')

    def send_message(self, message: bytes) -> None:
        self.server.sendto(message, self.server_address)

    @staticmethod
    def output(message, output_function, **kwargs):
        output_function(message, **kwargs)
