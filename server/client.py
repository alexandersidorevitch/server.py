import json

import socket, threading, time
from pprint import pprint

from config import CONFIG
from defs import Result, Action


class Client:
    def __init__(self, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT):
        self.server_address = address, port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_login = False

    def on_turn(self):
        return None

    def on_game(self):
        return None

    def on_player(self):
        return None

    def on_get_map(self):
        # To override
        return None

    def on_move(self):
        # To override
        return None

    def on_login(self):
        # To override
        self.is_login = True
        return None

    def on_logout(self):
        self.is_login = False
        return None

    def run_server(self):
        try:
            self.server.connect(self.server_address)
            shutdown = False
            while not shutdown:
                if self.is_login:
                    print('{}. Action.LOGOUT'.format(Action.LOGOUT))
                    print('{}. Action.MOVE'.format(Action.MOVE))
                    print('{}. Action.TURN'.format(Action.TURN))
                    print('{}. Action.PLAYER'.format(Action.PLAYER))
                    print('{}. Action.GAMES'.format(Action.GAMES))
                    print('{}. Action.MAP'.format(Action.MAP))
                else:
                    print('{}. Action.LOGIN'.format(Action.LOGIN))

                selected_action = None
                try:
                    selected_action = Action(int(input()))

                    method = self.ACTION_DICT[selected_action]
                    message = method(self)
                    converted_message = self.convert_message(selected_action, message)
                    pprint(converted_message)
                    self.send_message(converted_message)

                    result, message, data = self.receive_message()

                    if result == Result.OKEY:
                        print('Done')
                        print(message)
                    else:
                        print('Error {}'.format(result))

                    pprint('Received message: {}'.format(message))
                except ValueError as err:
                    print(err)
                except KeyError as err:
                    print('No functions for {} yet'.format(selected_action))
                except KeyboardInterrupt as err:
                    shutdown = True
                    print('End the code...')
        except json.decoder.JSONDecodeError as err:
            print(err)

        except Exception as err:
            print(err)
        finally:
            print('Close the connection...')
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

    ACTION_DICT = {
        Action.MAP: on_get_map,
        Action.MOVE: on_move,
        Action.LOGOUT: on_logout,
        Action.LOGIN: on_login,
        Action.TURN: on_turn,
        Action.GAMES: on_game,
        Action.PLAYER: on_player,
    }
