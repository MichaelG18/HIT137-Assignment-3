"""
HIT137 Assignment 3 - Image Puzzle Game
Core game logic and OOP implementation.

Author: Michael Ginis
"""


class PuzzleAction:
    """Base class for logical actions that can be applied to a puzzle."""

    def apply(self, game):
        """Apply the action to the supplied puzzle game."""
        raise NotImplementedError(
            "Subclasses must implement the apply() method."
        )


class SwapAction(PuzzleAction):
    """Logical action that swaps two tile positions."""

    def __init__(self, first_position, second_position):
        self.first_position = first_position
        self.second_position = second_position

    def apply(self, game):
        """Apply the swap without counting it as a player move."""
        game.swap_positions(
            self.first_position,
            self.second_position
        )


class RotateAction(PuzzleAction):
    """Logical action that rotates one tile clockwise."""

    def __init__(self, position):
        self.position = position

    def apply(self, game):
        """Apply the rotation without counting it as a player move."""
        game.rotate_position(self.position)


class FlipAction(PuzzleAction):
    """Logical action that flips one tile horizontally."""

    def __init__(self, position):
        self.position = position

    def apply(self, game):
        """Apply the flip without counting it as a player move."""
        game.flip_position(self.position)


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
        """Return the unique ID of the tile."""
        return self._tile_id

    @property
    def correct_position(self):
        """Return the tile's correct board position."""
        return self._correct_position

    @property
    def current_position(self):
        """Return the tile's current board position."""
        return self._current_position

    @current_position.setter
    def current_position(self, position):
        """Update the tile's current board position."""
        self._current_position = position

    @property
    def rotation(self):
        """Return the tile's current clockwise rotation."""
        return self._rotation

    @property
    def flipped(self):
        """Return whether the tile is horizontally flipped."""
        return self._flipped

    def is_correct(self):
        """Return True when position and orientation are correct."""
        return (
            self._current_position == self._correct_position
            and self._rotation == 0
            and not self._flipped
        )

    def rotate_clockwise(self):
        """Rotate the tile 90 degrees clockwise."""
        self._rotation = (self._rotation + 90) % 360

    def flip_horizontal(self):
        """Toggle the tile's horizontal flip state."""
        self._flipped = not self._flipped

    def reset_orientation(self):
        """Restore the tile to its original orientation."""
        self._rotation = 0
        self._flipped = False


class PuzzleGame:
    """Controls the state and core logic of the image puzzle game."""

    VALID_GRID_SIZES = (3, 4, 5)
    MAX_HINTS = 3

    def __init__(self, grid_size=3):
        self._grid_size = None
        self._tiles = []
        self._moves = 0
        self._selected_position = None
        self._hints_used = 0
        self._active_hint = None
        self._game_complete = False

        self.new_game(grid_size)

    @property
    def grid_size(self):
        """Return the current puzzle grid size."""
        return self._grid_size

    @property
    def moves(self):
        """Return the number of player moves made."""
        return self._moves

    @property
    def tiles(self):
        """Return a read-only view of the current tile sequence."""
        return tuple(self._tiles)

    @property
    def selected_position(self):
        """Return the currently selected tile position."""
        return self._selected_position

    @property
    def hints_used(self):
        """Return the number of hints used in the current game."""
        return self._hints_used

    @property
    def active_hint(self):
        """Return the currently displayed hint, if one exists."""
        return self._active_hint

    @property
    def game_complete(self):
        """Return whether the puzzle has been completed."""
        return self._game_complete

    def new_game(self, grid_size):
        """Create a fresh solved puzzle using the selected grid size."""
        if grid_size not in self.VALID_GRID_SIZES:
            raise ValueError("Grid size must be 3, 4 or 5.")

        self._grid_size = grid_size
        self._moves = 0
        self._selected_position = None
        self._hints_used = 0
        self._active_hint = None
        self._game_complete = False

        tile_count = grid_size * grid_size

        self._tiles = [
            Tile(tile_id=index, correct_position=index)
            for index in range(tile_count)
        ]

    def _validate_position(self, position):
        """Check that a board position is valid."""
        if not isinstance(position, int):
            raise TypeError("Tile position must be an integer.")

        if position < 0 or position >= len(self._tiles):
            raise IndexError("Tile position is outside the puzzle.")

    def tiles_left(self):
        """Return the number of tiles that are not currently correct."""
        return sum(
            not tile.is_correct()
            for tile in self._tiles
        )

    def is_complete(self):
        """Return True when every tile is correctly restored."""
        return self.tiles_left() == 0

    def swap_positions(self, first_position, second_position):
        """Swap two tile positions without counting a player move."""
        self._validate_position(first_position)
        self._validate_position(second_position)

        if first_position == second_position:
            return

        self._tiles[first_position], self._tiles[second_position] = (
            self._tiles[second_position],
            self._tiles[first_position],
        )

        self._tiles[first_position].current_position = first_position
        self._tiles[second_position].current_position = second_position

    def rotate_position(self, position):
        """Rotate a tile without counting a player move."""
        self._validate_position(position)
        self._tiles[position].rotate_clockwise()

    def flip_position(self, position):
        """Flip a tile horizontally without counting a player move."""
        self._validate_position(position)
        self._tiles[position].flip_horizontal()

    def apply_action(self, action):
        """
        Apply any PuzzleAction polymorphically.

        This is useful for setup transformations because these actions
        do not count towards the player's move total.
        """
        if not isinstance(action, PuzzleAction):
            raise TypeError("Action must be a PuzzleAction.")

        action.apply(self)
        self._update_completion()

    def select_or_swap(self, position):
        """
        Select, deselect, or swap tiles.

        First click selects a tile.
        Clicking the same tile again deselects it.
        Clicking a different second tile swaps the two tiles.
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

        self.swap_positions(first_position, second_position)

        self._selected_position = None
        self._moves += 1
        self._clear_active_hint()
        self._update_completion()

        return True

    def rotate_tile(self, position):
        """Rotate a tile 90 degrees clockwise as one player move."""
        self._validate_position(position)

        if self._game_complete:
            return False

        self.rotate_position(position)

        self._moves += 1
        self._selected_position = None
        self._clear_active_hint()
        self._update_completion()

        return True

    def flip_tile(self, position):
        """Flip a tile horizontally as one player move."""
        self._validate_position(position)

        if self._game_complete:
            return False

        self.flip_position(position)

        self._moves += 1
        self._selected_position = None
        self._clear_active_hint()
        self._update_completion()

        return True

    def request_hint(self):
        """
        Create a hint for one incorrect tile.

        Returns:
            (current_position, correct_position)

        Returns None when no hint can be supplied.
        """
        if self._game_complete:
            return None

        if self._hints_used >= self.MAX_HINTS:
            return None

        incorrect_tiles = [
            (position, tile)
            for position, tile in enumerate(self._tiles)
            if not tile.is_correct()
        ]

        if not incorrect_tiles:
            return None

        position, tile = incorrect_tiles[0]

        self._hints_used += 1
        self._active_hint = (
            position,
            tile.correct_position,
        )

        return self._active_hint

    def hints_remaining(self):
        """Return the number of hints still available."""
        return max(
            0,
            self.MAX_HINTS - self._hints_used
        )

    def _clear_active_hint(self):
        """Remove the current hint after a player move."""
        self._active_hint = None

    def _update_completion(self):
        """Update the stored completion state."""
        self._game_complete = self.is_complete()

        if self._game_complete:
            self._selected_position = None
            self._active_hint = None

    def solve(self):
        """
        Instantly restore the puzzle to its solved state.

        The move counter is cleared and further puzzle input is locked.
        """
        self._tiles.sort(
            key=lambda tile: tile.correct_position
        )

        for position, tile in enumerate(self._tiles):
            tile.current_position = position
            tile.reset_orientation()

        self._moves = 0
        self._selected_position = None
        self._active_hint = None
        self._game_complete = True

    def reset_game(self):
        """Reset the puzzle using the current grid size."""
        self.new_game(self._grid_size)
