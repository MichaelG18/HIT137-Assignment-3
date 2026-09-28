import cv2


class ImageProcessor:

    @staticmethod
    def load_image(file_path):
        image = cv2.imread(file_path)

        if image is None:
            raise ValueError("Unable to load image.")

        return image

    @staticmethod
    def prepare_image(image, grid_size, max_size=450):
        """
        Resize while preserving aspect ratio, centre-crop to a square,
        and ensure the final dimensions divide evenly by grid_size.
        """

        height, width = image.shape[:2]

        # Scale so the shortest side is at least max_size.
        scale = max_size / min(width, height)

        new_width = max(1, int(round(width * scale)))
        new_height = max(1, int(round(height * scale)))

        resized = cv2.resize(
            image,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA
            if scale < 1
            else cv2.INTER_LINEAR
        )

        # Centre crop to max_size x max_size.
        start_x = max(0, (new_width - max_size) // 2)
        start_y = max(0, (new_height - max_size) // 2)

        cropped = resized[
            start_y:start_y + max_size,
            start_x:start_x + max_size
        ]

        # Make final size divisible by grid size.
        final_size = (
            min(cropped.shape[0], cropped.shape[1])
            // grid_size
        ) * grid_size

        start_x = (cropped.shape[1] - final_size) // 2
        start_y = (cropped.shape[0] - final_size) // 2

        final_image = cropped[
            start_y:start_y + final_size,
            start_x:start_x + final_size
        ].copy()

        return final_image

    @staticmethod
    def split_into_tiles(image, grid_size):
        tile_height = image.shape[0] // grid_size
        tile_width = image.shape[1] // grid_size

        tiles = []

        for row in range(grid_size):
            tile_row = []

            for col in range(grid_size):
                y1 = row * tile_height
                y2 = y1 + tile_height

                x1 = col * tile_width
                x2 = x1 + tile_width

                tile_image = image[
                    y1:y2,
                    x1:x2
                ].copy()

                tile_row.append(tile_image)

            tiles.append(tile_row)

        return tiles