""" Game server.
"""
import json
import socket
from socketserver import BaseRequestHandler, ThreadingTCPServer
from threading import Thread
from typing import Any, Callable

from invoke import task

import errors
from config import CONFIG
from db import game_db
from defs import Action, Result
from entity.game import Game, GameState
from entity.serializable import Serializable
from entity.server_entity.server_observer import ServerObserver
from entity.server_entity.server_player import ServerPlayer
from logger import log


class AdditionalFunc:
    def __init__(self, start_function: Callable[[Any], None], stop_function: Callable[[Any], None]):
        self.__start_function = start_function
        self.__stop_function = stop_function

    def start(self, *args, **kwargs):
        self.__start_function(*args, **kwargs)

    def stop(self, *args, **kwargs):
        self.__stop_function(*args, **kwargs)


class GameServerRequestHandler(BaseRequestHandler):
    HANDLERS = {}

    def __init__(self, *args, **kwargs):
        self.action = None
        self.message_len = None
        self.message = None
        self.data = None
        self.server_role = None
        self.closed = None
        self._observer_notification_thread = None
        super(GameServerRequestHandler, self).__init__(*args, **kwargs)

    def setup(self):
        log.info('New connection from {}'.format(self.client_address))
        self.closed = False
        self.HANDLERS[id(self)] = self

    def handle(self):
        while not self.closed:
            data = self.request.recv(CONFIG.RECEIVE_CHUNK_SIZE)
            if data:
                self.data_received(data)
            else:
                self.closed = True

    def _observer_notification(self):
        while not self.closed and not (
                self.server_role.game is not None and self.server_role.game.state == GameState.FINISHED):
            try:
                if self.server_role.game:
                    log.debug('TICK!', game=self.server_role.game)
                    if self.server_role.game._start_tick_event.wait(CONFIG.TURN_TIMEOUT):
                        self.write_response(Result.OKEY, self.server_role.game.message_for_observer())
                        log.debug('DONE TICK!', game=self.server_role.game)
            except OSError:
                break

    def _start_observer_notification(self):
        self._observer_notification_thread = Thread(target=self._observer_notification)
        self._observer_notification_thread.start()

    def _stop_observer_notification(self):
        self._observer_notification_thread.join(CONFIG.TURN_TIMEOUT)

    @staticmethod
    def shutdown_all_sockets():
        for handler in GameServerRequestHandler.HANDLERS.values():
            handler.request.shutdown(socket.SHUT_RDWR)

    @property
    def game(self):
        return self.server_role.game if self.server_role is not None else None

    def finish(self):
        log.warn('Connection from {} lost'.format(self.client_address),
                 game=self.game)
        if self.server_role is not None:
            if self.game is not None:
                self.game.remove_instance(self.server_role)
            self.stop_additional_functions()
            if self.server_role.save_to_db:
                game_db.add_action(self.game.game_idx, Action.LOGOUT,
                                   player_idx=self.server_role.instance.idx)
        self.HANDLERS.pop(id(self))

    def data_received(self, data):
        if self.data:
            data = self.data + data
            self.data = None

        if self.parse_data(data):
            log.info('[REQUEST] {}: {}, action: {!r}, message:\n{}'.format(
                self.server_role.class_name if self.server_role is not None else 'Connection',
                self.server_role.instance.idx if self.server_role is not None else self.client_address,
                Action(self.action), self.message),
                game=self.game)

            try:
                data = json.loads(self.message)
                if not isinstance(data, dict):
                    raise errors.BadCommand('The command\'s payload is not a dictionary')

                if self.server_role is None:
                    self.create_role_by_login_action()

                self.write_response(*self.server_role.action(self.action, data))

                if self.action in self.REPLAY_ACTIONS and self.server_role.save_to_db:
                    game_db.add_action(self.game.game_idx, self.action, message=data,
                                       player_idx=self.server_role.instance.idx)

            # Handle errors:
            except (json.decoder.JSONDecodeError, errors.BadCommand) as err:
                self.error_response(Result.BAD_COMMAND, err)
            except errors.AccessDenied as err:
                self.error_response(Result.ACCESS_DENIED, err)
            except errors.InappropriateGameState as err:
                self.error_response(Result.INAPPROPRIATE_GAME_STATE, err)
            except errors.Timeout as err:
                self.error_response(Result.TIMEOUT, err)
            except errors.ResourceNotFound as err:
                self.error_response(Result.RESOURCE_NOT_FOUND, err)
            except Exception:
                log.exception('Got unhandled exception on client command execution',
                              game=self.game)
                self.error_response(Result.INTERNAL_SERVER_ERROR)
            finally:
                self.action = None
                self.message_len = None
                self.message = None

    def parse_data(self, data):
        """ Parses input command.
        returns: True if command parsing completed
        """
        # Read action:
        if self.action is None:
            if len(data) < CONFIG.ACTION_HEADER:
                self.data = data
                return False
            self.action = Action(int.from_bytes(data[0:CONFIG.ACTION_HEADER], byteorder='little'))
            data = data[CONFIG.ACTION_HEADER:]

        # Read size of message:
        if self.message_len is None:
            if len(data) < CONFIG.MSGLEN_HEADER:
                self.data = data
                return False
            self.message_len = int.from_bytes(data[0:CONFIG.MSGLEN_HEADER], byteorder='little')
            data = data[CONFIG.MSGLEN_HEADER:]

        # Read message:
        if self.message is None:
            if len(data) < self.message_len:
                self.data = data
                return False
            self.message = data[0:self.message_len].decode('utf-8') or '{}'
            self.data = data[self.message_len:]

        return True

    def write_response(self, result, message=None):
        resp_message = '' if message is None else message
        log.debug('[RESPONSE] {}: {}, result: {!r}, message:\n{}'.format(
            self.server_role.class_name,
            self.server_role.instance.idx if self.server_role is not None and self.server_role.instance is not None else
            self.client_address,
            result, resp_message), game=self.game)
        self.request.sendall(result.to_bytes(CONFIG.RESULT_HEADER, byteorder='little'))
        self.request.sendall(len(resp_message).to_bytes(CONFIG.MSGLEN_HEADER, byteorder='little'))
        self.request.sendall(resp_message.encode('utf-8'))

    def error_response(self, result, exception=None):
        if exception is not None:
            str_exception = str(exception)
            log.error(str_exception, game=self.game)
            error = Serializable()
            error.set_attributes(error=str_exception)
            response_msg = error.to_json_str()
        else:
            response_msg = None
        self.write_response(result, response_msg)

    def get_role_by_login_action(self):
        for role in self.ROLES:
            if self.action == role.LOGIN_ACTION:
                return role
        return None

    def create_role_by_login_action(self):
        server_role = self.get_role_by_login_action()
        if server_role is None:
            return errors.ResourceNotFound('No any server roles with login action {}'.format(self.action.name))
        log.debug('Add role')
        self.server_role = server_role()
        log.debug('{}'.format(self.server_role))
        self.start_additional_functions()

    def start_additional_functions(self):
        for role, functions in self.ADDITIONAL_FUNCTION.items():
            if isinstance(self.server_role, role):
                for function in functions:
                    function.start(self)
                break

    def stop_additional_functions(self):
        for role, functions in self.ADDITIONAL_FUNCTION.items():
            if isinstance(self.server_role, role):
                for function in functions:
                    function.stop(self)
                break

    REPLAY_ACTIONS = {
        Action.LOGIN,
        Action.LOGOUT,
        Action.MOVE,
        Action.UPGRADE,
    }
    ROLES = {
        ServerPlayer,
        ServerObserver
    }
    ADDITIONAL_FUNCTION = {
        ServerPlayer: (),
        ServerObserver: (AdditionalFunc(_observer_notification, _stop_observer_notification),),
    }


@task
def run_server(_, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT, log_level='INFO'):
    """ Launches 'WG Forge' TCP server.
    """
    log.setLevel(log_level)
    ThreadingTCPServer.allow_reuse_address = True
    server = ThreadingTCPServer((address, port), GameServerRequestHandler)
    log.info('Serving on {}'.format(server.socket.getsockname()))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.warn('Server stopped by keyboard interrupt, shutting down...')
    finally:
        try:
            GameServerRequestHandler.shutdown_all_sockets()
            Game.stop_all_games()
            if log.is_queued:
                log.stop()
        finally:
            server.shutdown()
            server.server_close()
