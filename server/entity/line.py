""" Graph edge entity - Line.
"""
from entity.serializable import Serializable


class Line(Serializable):
    """ Line entity defined by: two points (p0, p1), length, unique id.
    """
    def __init__(self, idx, length=0, p0=None, p1=None):
        self.idx = idx
        self.length = length
        self.points = (p0, p1)

    def __repr__(self):
        return '<Line(idx={}, length={}, points={})>'.format(self.idx, self.length, self.points)
