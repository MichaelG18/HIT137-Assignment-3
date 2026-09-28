import random
import numpy as np

from tile import Tile
from image_processor import ImageProcessor


class Puzzle:
    def __init__(self, image, grid_size):
        self.grid_size = grid_size

        self.original_image = ImageProcessor.prepare_image(
            image,
            grid_size
        )

        self.tiles = []

        self._create_tiles()

    def _create_tiles(self):
        tile_images = ImageProcessor.split_into_tiles(
            self.original_image,
            self.grid_size
        )

        self.tiles = []

        for row in range(self.grid_size):
            tile_row = []

            for col in range(self.grid_size):
                tile = Tile(
                    tile_images[row][col],
                    row,
                    col
                )

                tile_row.append(tile)

            self.tiles.append(tile_row)

    # ---------------------------------------------------------
    # SWAP
    # ---------------------------------------------------------

    def swap_tiles(self, row1, col1, row2, col2):
        self.tiles[row1][col1], self.tiles[row2][col2] = (
            self.tiles[row2][col2],
            self.tiles[row1][col1]
        )

    # ---------------------------------------------------------
    # ROTATE
    # ---------------------------------------------------------

    def rotate_tile(self, row, col, degrees=90):
        self.tiles[row][col].rotate(degrees)

    # ---------------------------------------------------------
    # FLIP
    # ---------------------------------------------------------

    def flip_tile_horizontal(self, row, col):
        self.tiles[row][col].flip_horizontal()

    def flip_tile_vertical(self, row, col):
        self.tiles[row][col].flip_vertical()

    # ---------------------------------------------------------
    # SCRAMBLE
    # ---------------------------------------------------------

    def scramble(self):
        transformation_counts = {
            3: 6,
            4: 12,
            5: 20
        }

        number_of_transformations = transformation_counts[
            self.grid_size
        ]

        # Guarantee at least one of every required transformation.
        transformations = [
            "swap",
            "rotate",
            "flip"
        ]

        while len(transformations) < number_of_transformations:
            transformations.append(
                random.choice(["swap", "rotate", "flip"])
            )

        random.shuffle(transformations)

        for transformation in transformations:

            if transformation == "swap":
                self._random_swap()

            elif transformation == "rotate":
                self._random_rotate()

            elif transformation == "flip":
                self._random_flip()

        # Extremely unlikely, but avoid presenting an already solved puzzle.
        if self.is_solved():
            self._random_swap()

    def _random_swap(self):
        positions = [
            (row, col)
            for row in range(self.grid_size)
            for col in range(self.grid_size)
        ]

        first, second = random.sample(positions, 2)

        self.swap_tiles(
            first[0],
            first[1],
            second[0],
            second[1]
        )

    def _random_rotate(self):
        row = random.randrange(self.grid_size)
        col = random.randrange(self.grid_size)

        degrees = random.choice(
            [90, 180, 270]
        )

        self.rotate_tile(
            row,
            col,
            degrees
        )

    def _random_flip(self):
        row = random.randrange(self.grid_size)
        col = random.randrange(self.grid_size)

        if random.choice([True, False]):
            self.flip_tile_horizontal(row, col)
        else:
            self.flip_tile_vertical(row, col)

    # ---------------------------------------------------------
    # CORRECTNESS
    # ---------------------------------------------------------

    def is_tile_correct(self, row, col):
        return self.tiles[row][col].is_correct(
            row,
            col
        )

    def get_incorrect_count(self):
        count = 0

        for row in range(self.grid_size):
            for col in range(self.grid_size):

                if not self.is_tile_correct(row, col):
                    count += 1

        return count

    def is_solved(self):
        return self.get_incorrect_count() == 0

    # ---------------------------------------------------------
    # DISPLAY IMAGE
    # ---------------------------------------------------------

    def get_display_image(self):
        image_rows = []

        for row in self.tiles:
            images = [
                tile.image
                for tile in row
            ]

            image_rows.append(
                np.hstack(images)
            )

        return np.vstack(image_rows)

    # ---------------------------------------------------------
    # HINT
    # ---------------------------------------------------------

    def get_hint(self):
        incorrect_positions = []

        for row in range(self.grid_size):
            for col in range(self.grid_size):

                if not self.is_tile_correct(row, col):
                    incorrect_positions.append(
                        (row, col)
                    )

        if not incorrect_positions:
            return None

        current_position = random.choice(
            incorrect_positions
        )

        row, col = current_position

        tile = self.tiles[row][col]

        home_position = (
            tile.original_row,
            tile.original_col
        )

        return current_position, home_position

    # ---------------------------------------------------------
    # SOLVE
    # ---------------------------------------------------------

    def solve(self):
        self._create_tiles()