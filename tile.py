import cv2
import numpy as np


class Tile:
    """Represents one image tile within the puzzle."""

    def __init__(self, image, original_row, original_col):
        # Store both the untouched original tile and the working image.
        self.original_image = image.copy()
        self.image = image.copy()

        self.original_row = original_row
        self.original_col = original_col

        # Transformation state is retained because it is useful for
        # tracking and applying puzzle operations.
        self.rotation = 0
        self.flipped_horizontal = False
        self.flipped_vertical = False

    def rotate(self, degrees=90):
        """Rotate the tile clockwise by a multiple of 90 degrees."""
        turns = (degrees // 90) % 4

        for _ in range(turns):
            self.image = cv2.rotate(
                self.image,
                cv2.ROTATE_90_CLOCKWISE
            )

        self.rotation = (self.rotation + degrees) % 360

    def flip_horizontal(self):
        """Flip the tile horizontally."""
        self.image = cv2.flip(self.image, 1)
        self.flipped_horizontal = not self.flipped_horizontal

    def flip_vertical(self):
        """Flip the tile vertically."""
        self.image = cv2.flip(self.image, 0)
        self.flipped_vertical = not self.flipped_vertical

    def is_correct(self, current_row, current_col):
        """
        Return True when the tile is in its original grid position
        and its displayed image matches its original orientation.

        Pixel comparison is used rather than relying only on the
        transformation history. This correctly handles equivalent
        combinations of rotations and flips that produce the same
        final visual orientation.
        """

        # The tile must first be in its correct grid position.
        if (
            self.original_row != current_row
            or self.original_col != current_col
        ):
            return False

        # The tile must also visually match its original orientation.
        return np.array_equal(
            self.image,
            self.original_image
        )
