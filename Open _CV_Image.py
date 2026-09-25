import cv2
import numpy as np
import random


# -----------------------------
# RESIZE IMAGE
# -----------------------------
def resize_to_screen(image, max_width=900, max_height=700):
    h, w = image.shape[:2]

    scale = min(max_width / w, max_height / h)

    if scale < 1:
        new_w = int(w * scale)
        new_h = int(h * scale)

        image = cv2.resize(
            image,
            (new_w, new_h),
            interpolation=cv2.INTER_AREA
        )

    return image


# -----------------------------
# PAD IMAGE FOR GRID
# -----------------------------
def pad_for_grid(image, grid_size):
    h, w = image.shape[:2]

    new_w = ((w + grid_size - 1) // grid_size) * grid_size
    new_h = ((h + grid_size - 1) // grid_size) * grid_size

    pad_right = new_w - w
    pad_bottom = new_h - h

    padded = cv2.copyMakeBorder(
        image,
        0,
        pad_bottom,
        0,
        pad_right,
        cv2.BORDER_CONSTANT,
        value=(0, 0, 0)
    )

    return padded


# -----------------------------
# SPLIT INTO TILES
# -----------------------------
def split_into_tiles(image, grid_size):
    h, w = image.shape[:2]

    tile_h = h // grid_size
    tile_w = w // grid_size

    tiles = []

    for row in range(grid_size):
        for col in range(grid_size):

            y1 = row * tile_h
            y2 = y1 + tile_h

            x1 = col * tile_w
            x2 = x1 + tile_w

            tile = image[y1:y2, x1:x2].copy()

            tiles.append(tile)

    return tiles


# -----------------------------
# ROTATE TILE
# -----------------------------
def rotate_tile(tile):
    angle = random.choice([90, 180, 270])

    if angle == 90:
        tile = cv2.rotate(tile, cv2.ROTATE_90_CLOCKWISE)

    elif angle == 180:
        tile = cv2.rotate(tile, cv2.ROTATE_180)

    else:
        tile = cv2.rotate(tile, cv2.ROTATE_90_COUNTERCLOCKWISE)

    return tile


# -----------------------------
# FLIP TILE
# -----------------------------
def flip_tile(tile):
    flip_code = random.choice([0, 1])

    return cv2.flip(tile, flip_code)


# -----------------------------
# NUMBER OF TRANSFORMATIONS
# -----------------------------
def get_transform_count(grid_size):
    if grid_size == 3:
        return 6
    elif grid_size == 4:
        return 12
    elif grid_size == 5:
        return 20
    return 6


# -----------------------------
# SCRAMBLE TILES
# -----------------------------
def scramble_tiles(tiles, grid_size):

    operations_log = []

    num_operations = get_transform_count(grid_size)

    for _ in range(num_operations):

        operation = random.choice(
            ["swap", "rotate", "flip"]
        )

        # SWAP
        if operation == "swap":

            idx1, idx2 = random.sample(
                range(len(tiles)),
                2
            )

            tiles[idx1], tiles[idx2] = (
                tiles[idx2],
                tiles[idx1]
            )

            operations_log.append(
                f"SWAP Tile {idx1} <-> Tile {idx2}"
            )

        # ROTATE
        elif operation == "rotate":

            idx = random.randint(
                0,
                len(tiles) - 1
            )

            tiles[idx] = rotate_tile(
                tiles[idx]
            )

            operations_log.append(
                f"ROTATE Tile {idx}"
            )

        # FLIP
        else:

            idx = random.randint(
                0,
                len(tiles) - 1
            )

            tiles[idx] = flip_tile(
                tiles[idx]
            )

            operations_log.append(
                f"FLIP Tile {idx}"
            )

    return tiles, operations_log


# -----------------------------
# REBUILD IMAGE
# -----------------------------
def rebuild_image(tiles, grid_size):

    rows = []

    for row in range(grid_size):

        start = row * grid_size
        end = start + grid_size

        row_tiles = np.hstack(
            tiles[start:end]
        )

        rows.append(row_tiles)

    final_image = np.vstack(rows)

    return final_image


# -----------------------------
# MAIN PROGRAM
# -----------------------------
def main():

    image_path = input(
        "Enter image filename/path: "
    )

    image = cv2.imread(image_path)

    if image is None:
        print("Could not load image.")
        return

    print("\nChoose Grid Size:")
    print("1. 3 x 3")
    print("2. 4 x 4")
    print("3. 5 x 5")

    choice = input("Selection: ")

    if choice == "1":
        grid_size = 3
    elif choice == "2":
        grid_size = 4
    elif choice == "3":
        grid_size = 5
    else:
        print("Invalid choice. Defaulting to 3x3.")
        grid_size = 3

    # Resize
    image = resize_to_screen(image)

    # Pad
    image = pad_for_grid(
        image,
        grid_size
    )

    # Split
    tiles = split_into_tiles(
        image,
        grid_size
    )

    # Scramble
    tiles, operations = scramble_tiles(
        tiles,
        grid_size
    )

    # Reassemble
    scrambled_image = rebuild_image(
        tiles,
        grid_size
    )

    print("\nTransformations Applied:")
    for op in operations:
        print(op)

    cv2.imshow(
        "Original Image",
        image
    )

    cv2.imshow(
        "Scrambled Puzzle",
        scrambled_image
    )

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()