from abc import ABCMeta
from abc import abstractmethod


class AbstractClient(metaclass=ABCMeta):

    @abstractmethod
    def run_server(self) -> None:
        """ Starts the server
        """
        pass

    @abstractmethod
    def receive_message(self) -> dict:
        """ Accepts a message from a connected server
        """
        pass

    @abstractmethod
    def send_message(self, message: bytes) -> None:
        """ Sends a message to the connected server
        """
        pass
