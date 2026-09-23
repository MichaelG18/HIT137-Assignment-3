"""
HIT137 Assignment 3 - Image Puzzle Game
Core game logic and OOP implementation.

Author: Michael Ginis
"""


class Tile:
    """Represents one tile within the image puzzle."""

    def __init__(self, tile_id, correct_position):
        self._tile_id = tile_id
        self._correct_position = correct_position
        self._current_position = correct_position
        self._rotation = 0
        self._flipped = False

    @property
    def tile_id(self):
        return self._tile_id

    @property
    def correct_position(self):
        return self._correct_position

    @property
    def current_position(self):
        return self._current_position

    @current_position.setter
    def current_position(self, position):
        self._current_position = position

    @property
    def rotation(self):
        return self._rotation

    @property
    def flipped(self):
        return self._flipped

    def is_correct(self):
        """Return True when the tile is in its original position and orientation."""
        return (
            self._current_position == self._correct_position
            and self._rotation == 0
            and not self._flipped
        )
