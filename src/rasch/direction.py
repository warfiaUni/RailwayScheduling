from enum import Enum


class Direction(Enum):
    """ Representation of directions.

    Starting north as 0 and each 90 degree rotation adds 1.
    """
    n = 0
    """ North"""
    e = 1
    """ East"""
    s = 2
    """ South"""
    w = 3
    """ West"""
