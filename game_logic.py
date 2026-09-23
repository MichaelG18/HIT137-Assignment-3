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

    def rotate_clockwise(self):
        """Rotate the tile 90 degrees clockwise."""
        self._rotation = (self._rotation + 90) % 360

    def flip_horizontal(self):
        """Toggle the horizontal flip state of the tile."""
        self._flipped = not self._flipped


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

    def _validate_position(self, position):
        """Check that a tile position exists in the current puzzle."""
        if not isinstance(position, int):
            raise TypeError("Tile position must be an integer.")

        if position < 0 or position >= len(self._tiles):
            raise IndexError("Tile position is outside the puzzle.")

    def select_or_swap(self, position):
        """
        Select a tile or swap it with the previously selected tile.

        First click: select the tile.
        Same tile again: deselect it.
        Different second tile: swap the two tiles.
        """
        self._validate_position(position)

        if self._game_complete:
            return False

        if self._selected_position is None:
            self._selected_position = position
            return False

        if self._selected_position == position:
            self._selected_position = None
            return False

        first_position = self._selected_position
        second_position = position

        self._tiles[first_position], self._tiles[second_position] = (
            self._tiles[second_position],
            self._tiles[first_position],
        )

        self._tiles[first_position].current_position = first_position
        self._tiles[second_position].current_position = second_position

        self._selected_position = None
        self._moves += 1

        self._update_completion()
        return True

    def rotate_tile(self, position):
        """Rotate a tile 90 degrees clockwise."""
        self._validate_position(position)

        if self._game_complete:
            return False

        tile = self._tiles[position]
        tile.rotate_clockwise()

        self._moves += 1
        self._selected_position = None

        self._update_completion()
        return True

    def flip_tile(self, position):
        """Flip a tile horizontally."""
        self._validate_position(position)

        if self._game_complete:
            return False

        tile = self._tiles[position]
        tile.flip_horizontal()

        self._moves += 1
        self._selected_position = None

        self._update_completion()
        return True

    def _update_completion(self):
        """Update the completion state of the current puzzle."""
        self._game_complete = self.is_complete()
