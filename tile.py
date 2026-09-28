import cv2


class Tile:
    def __init__(self, image, original_row, original_col):
        self.image = image.copy()

        self.original_row = original_row
        self.original_col = original_col

        self.rotation = 0
        self.flipped_horizontal = False
        self.flipped_vertical = False

    def rotate(self, degrees=90):
        turns = (degrees // 90) % 4

        for _ in range(turns):
            self.image = cv2.rotate(
                self.image,
                cv2.ROTATE_90_CLOCKWISE
            )

        self.rotation = (self.rotation + degrees) % 360

    def flip_horizontal(self):
        self.image = cv2.flip(self.image, 1)
        self.flipped_horizontal = not self.flipped_horizontal

    def flip_vertical(self):
        self.image = cv2.flip(self.image, 0)
        self.flipped_vertical = not self.flipped_vertical

    def is_correct(self, current_row, current_col):
        return (
            self.original_row == current_row
            and self.original_col == current_col
            and self.rotation == 0
            and not self.flipped_horizontal
            and not self.flipped_vertical
        )