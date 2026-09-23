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

class PuzzleGame:
    """Controls the main state and logic of the image puzzle game."""

    VALID_GRID_SIZES = (3, 4, 5)

    def __init__(self, grid_size=3):
        self._grid_size = None
        self._tiles = []
        self._moves = 0
        self._selected_position = None
        self._hints_used = 0
        self._game_complete = False

        self.new_game(grid_size)

    @property
    def grid_size(self):
        return self._grid_size

    @property
    def moves(self):
        return self._moves

    @property
    def tiles(self):
        return tuple(self._tiles)

    @property
    def selected_position(self):
        return self._selected_position

    @property
    def hints_used(self):
        return self._hints_used

    @property
    def game_complete(self):
        return self._game_complete

    def new_game(self, grid_size):
        """Create a fresh puzzle using the selected grid size."""

        if grid_size not in self.VALID_GRID_SIZES:
            raise ValueError("Grid size must be 3, 4 or 5.")

        self._grid_size = grid_size
        self._moves = 0
        self._selected_position = None
        self._hints_used = 0
        self._game_complete = False

        tile_count = grid_size * grid_size

        self._tiles = [
            Tile(tile_id=index, correct_position=index)
            for index in range(tile_count)
        ]

    def tiles_left(self):
        """Return the number of tiles that are not currently correct."""
        return sum(not tile.is_correct() for tile in self._tiles)

    def is_complete(self):
        """Return True when every tile is correctly restored."""
        return self.tiles_left() == 0
