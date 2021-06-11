import json

import socket, threading, time

from config import CONFIG
from defs import Result, Action


class Client:
    MAP_LAYERS = {0, 1, 10}

    def __init__(self, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT):
        self.server_address = address, port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.idx = ''
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
        """ Triggered when the turn event is called
        """
        return None

    def on_game(self):
        """ Triggered when the game event is called
        """
        return None

    def on_player(self):
        """ Triggered when the player event is called
        """
        return None

    def on_logout(self):
        """ Triggered when the logout event is called
        """
        return None

    def on_get_map(self):
        """ Triggered when the map event is called
        """
        # To override
        raise NotImplementedError('Needs to redefine the method in the child class')

    def on_move(self):
        """ Triggered when the move event is called
        """
        # To override
        raise NotImplementedError('Needs to redefine the method in the child class')

    def on_login(self):
        """ Triggered when the login event is called
        """
        # To override
        raise NotImplementedError('Needs to redefine the method in the child class')

    def run_server(self):
        """ Starts the server
        """
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

                    if selected_action == Action.LOGIN:
                        self.idx = message.get('idx')

                    Client.output('Received message: ', CONFIG.DEFAULT_OUTPUT_FUNCTION)
                    Client.output(Client.get_pretty_string(message), CONFIG.DEFAULT_OUTPUT_FUNCTION)
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
        """ Accepts a message from a connected server
        """
        data = b''
        while len(data) < CONFIG.RESULT_HEADER + CONFIG.MSGLEN_HEADER:
            data += self.server.recv(CONFIG.RECEIVE_CHUNK_SIZE)

        result = Result(int.from_bytes(data[0:CONFIG.ACTION_HEADER], byteorder='little'))

        data = data[CONFIG.ACTION_HEADER:]
        message_len = int.from_bytes(data[0:CONFIG.MSGLEN_HEADER], byteorder='little')

        message = data[CONFIG.MSGLEN_HEADER:]
        while len(message) < message_len:
            message += self.server.recv(CONFIG.RECEIVE_CHUNK_SIZE)
        return result, json.loads(message.decode('utf-8') or '{}'), message[message_len:]

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
            dump_message).to_bytes(length=CONFIG.MSGLEN_HEADER,
                                   byteorder='little') + dump_message.encode(
            'utf-8')

    def send_message(self, message: bytes) -> None:
        """ Sends a message to the connected server
        """
        self.server.sendto(message, self.server_address)

    @staticmethod
    def output(message, output_function, **kwargs):
        """ Outputs a message using an auxiliary function
        """
        output_function(message, **kwargs)

    @staticmethod
    def get_pretty_string(message):
        """ Returns pretty performance of message
        """
        from pprint import pprint
        from io import StringIO
        f = StringIO()
        pprint(message, f)
        return f.getvalue()
