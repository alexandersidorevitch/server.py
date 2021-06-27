""" Observer Entity. Handles requests when client connects to server as OBSERVER to watch replay(s).
"""
import uuid
from threading import Lock

from entity.serializable import Serializable


class Observer(Serializable):
    PROTECTED = {'lock', }

    def __init__(self, name, idx=None):
        self.idx = str(uuid.uuid4()) if idx is None else idx
        self.name = name
        self.lock = Lock()

    def __repr__(self):
        return '<Observer name: {}>'.format(self.name)
