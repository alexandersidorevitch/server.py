from player import Player
from config import CONFIG
from defs import Action


class Observer(Player):
    def __init__(self, address=CONFIG.SERVER_ADDR, port=CONFIG.SERVER_PORT, log_level='INFO'):
        super().__init__(address, port, log_level)
        self.ACTION_DICT = {
            Action.OBSERVER: self.on_observer,
            Action.GAME: self.on_game
        }

    def on_observer(self):
        return None

    def on_game(self):
        self.logger.info('Input game_idx:')
        return {'game_idx': int(input())}
