import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import cv2
from PIL import Image, ImageTk

from image_processor import ImageProcessor
from puzzle import Puzzle


class PuzzleApp:

    def __init__(self, root):
        self.root = root

        self.root.title("HIT137 Image Puzzle")
        self.root.geometry("1050x700")

        self.puzzle = None

        self.selected_tile = None

        self.moves = 0

        self.hints_remaining = 3

        self.hint_current = None
        self.hint_home = None

        self.game_finished = False

        self.original_photo = None
        self.puzzle_photo = None

        self.grid_var = tk.StringVar(
            value="3 x 3"
        )

        self.moves_var = tk.StringVar(
            value="Moves: 0"
        )

        self.incorrect_var = tk.StringVar(
            value="Incorrect tiles: 0"
        )

        self.hint_var = tk.StringVar(
            value="Hint (3 remaining)"
        )

        self.create_interface()

    # =========================================================
    # INTERFACE
    # =========================================================

    def create_interface(self):

        main = ttk.Frame(
            self.root,
            padding=15
        )

        main.pack(
            fill=tk.BOTH,
            expand=True
        )

        title = ttk.Label(
            main,
            text="Image Puzzle Game",
            font=("Arial", 22, "bold")
        )

        title.pack(pady=10)

        # -----------------------------------------------------
        # Controls
        # -----------------------------------------------------

        controls = ttk.Frame(main)

        controls.pack(pady=10)

        ttk.Label(
            controls,
            text="Grid Size:"
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        self.grid_combo = ttk.Combobox(
            controls,
            textvariable=self.grid_var,
            values=[
                "3 x 3",
                "4 x 4",
                "5 x 5"
            ],
            state="readonly",
            width=10
        )

        self.grid_combo.pack(
            side=tk.LEFT,
            padx=5
        )

        ttk.Button(
            controls,
            text="Load Image",
            command=self.load_image
        ).pack(
            side=tk.LEFT,
            padx=10
        )

        # -----------------------------------------------------
        # Image area
        # -----------------------------------------------------

        image_area = ttk.Frame(main)

        image_area.pack(
            fill=tk.BOTH,
            expand=True
        )

        original_frame = ttk.LabelFrame(
            image_area,
            text="Original Image"
        )

        original_frame.pack(
            side=tk.LEFT,
            padx=10
        )

        self.original_canvas = tk.Canvas(
            original_frame,
            width=450,
            height=450,
            bg="white"
        )

        self.original_canvas.pack()

        puzzle_frame = ttk.LabelFrame(
            image_area,
            text="Puzzle Image"
        )

        puzzle_frame.pack(
            side=tk.LEFT,
            padx=10
        )

        self.puzzle_canvas = tk.Canvas(
            puzzle_frame,
            width=450,
            height=450,
            bg="white"
        )

        self.puzzle_canvas.pack()

        # -----------------------------------------------------
        # Mouse controls
        # -----------------------------------------------------

        self.puzzle_canvas.bind(
            "<Button-1>",
            self.left_click
        )

        self.puzzle_canvas.bind(
            "<Button-3>",
            self.right_click
        )

        self.puzzle_canvas.bind(
            "<Shift-Button-1>",
            self.shift_left_click
        )

        # -----------------------------------------------------
        # Score
        # -----------------------------------------------------

        score = ttk.Frame(main)

        score.pack(pady=10)

        ttk.Label(
            score,
            textvariable=self.moves_var,
            font=("Arial", 12, "bold")
        ).pack(
            side=tk.LEFT,
            padx=30
        )

        ttk.Label(
            score,
            textvariable=self.incorrect_var,
            font=("Arial", 12, "bold")
        ).pack(
            side=tk.LEFT,
            padx=30
        )

        # -----------------------------------------------------
        # Buttons
        # -----------------------------------------------------

        buttons = ttk.Frame(main)

        buttons.pack(pady=5)

        self.hint_button = ttk.Button(
            buttons,
            textvariable=self.hint_var,
            command=self.show_hint,
            state=tk.DISABLED
        )

        self.hint_button.pack(
            side=tk.LEFT,
            padx=10
        )

        self.solve_button = ttk.Button(
            buttons,
            text="Solve",
            command=self.solve,
            state=tk.DISABLED
        )

        self.solve_button.pack(
            side=tk.LEFT,
            padx=10
        )

        instructions = (
            "Left click: Select/Swap    |    "
            "Right click: Rotate    |    "
            "Shift + Left click: Flip"
        )

        ttk.Label(
            main,
            text=instructions
        ).pack(pady=5)

    # =========================================================
    # LOAD IMAGE
    # =========================================================

    def load_image(self):

        file_path = filedialog.askopenfilename(
            filetypes=[
                (
                    "Images",
                    "*.jpg *.jpeg *.png *.bmp"
                )
            ]
        )

        if not file_path:
            return

        try:
            image = ImageProcessor.load_image(
                file_path
            )

        except ValueError as error:

            messagebox.showerror(
                "Error",
                str(error)
            )

            return

        grid_size = int(
            self.grid_var.get()[0]
        )

        self.puzzle = Puzzle(
            image,
            grid_size
        )

        self.puzzle.scramble()

        self.moves = 0
        self.hints_remaining = 3

        self.selected_tile = None

        self.hint_current = None
        self.hint_home = None

        self.game_finished = False

        self.hint_button.config(
            state=tk.NORMAL
        )

        self.solve_button.config(
            state=tk.NORMAL
        )

        self.refresh()

    # =========================================================
    # LEFT CLICK
    # =========================================================

    def left_click(self, event):

        if self.puzzle is None:
            return

        if self.game_finished:
            return

        row, col = self.get_tile_position(
            event.x,
            event.y
        )

        clicked = (row, col)

        if self.selected_tile is None:

            self.selected_tile = clicked
            self.draw_puzzle()

            return

        if self.selected_tile == clicked:

            self.selected_tile = None
            self.draw_puzzle()

            return

        old_row, old_col = (
            self.selected_tile
        )

        self.puzzle.swap_tiles(
            old_row,
            old_col,
            row,
            col
        )

        self.selected_tile = None

        self.moves += 1

        self.after_move()

    # =========================================================
    # RIGHT CLICK
    # =========================================================

    def right_click(self, event):

        if (
            self.puzzle is None
            or self.game_finished
        ):
            return

        row, col = self.get_tile_position(
            event.x,
            event.y
        )

        self.puzzle.rotate_tile(
            row,
            col,
            90
        )

        self.moves += 1

        self.after_move()

    # =========================================================
    # SHIFT + LEFT CLICK
    # =========================================================

    def shift_left_click(
        self,
        event
    ):

        if (
            self.puzzle is None
            or self.game_finished
        ):
            return "break"

        row, col = self.get_tile_position(
            event.x,
            event.y
        )

        self.puzzle.flip_tile_horizontal(
            row,
            col
        )

        self.moves += 1

        self.after_move()

        return "break"

    # =========================================================
    # TILE POSITION
    # =========================================================

    def get_tile_position(
        self,
        x,
        y
    ):

        image_size = (
            self.puzzle.original_image.shape[0]
        )

        tile_size = (
            image_size /
            self.puzzle.grid_size
        )

        row = int(y // tile_size)
        col = int(x // tile_size)

        row = min(
            max(row, 0),
            self.puzzle.grid_size - 1
        )

        col = min(
            max(col, 0),
            self.puzzle.grid_size - 1
        )

        return row, col

    # =========================================================
    # AFTER MOVE
    # =========================================================

    def after_move(self):

        # Hint disappears after next move.
        self.hint_current = None
        self.hint_home = None

        self.refresh()

        if self.puzzle.is_solved():

            self.game_finished = True

            self.hint_button.config(
                state=tk.DISABLED
            )

            self.solve_button.config(
                state=tk.DISABLED
            )

            messagebox.showinfo(
                "Puzzle Complete",
                f"Congratulations!\n\n"
                f"Puzzle solved in "
                f"{self.moves} moves."
            )

    # =========================================================
    # REFRESH
    # =========================================================

    def refresh(self):

        self.draw_original()
        self.draw_puzzle()

        self.moves_var.set(
            f"Moves: {self.moves}"
        )

        incorrect = (
            self.puzzle
            .get_incorrect_count()
        )

        self.incorrect_var.set(
            f"Incorrect tiles: "
            f"{incorrect}"
        )

        self.hint_var.set(
            f"Hint "
            f"({self.hints_remaining} remaining)"
        )

    # =========================================================
    # ORIGINAL IMAGE
    # =========================================================

    def draw_original(self):

        self.original_canvas.delete(
            "all"
        )

        self.original_photo = (
            self.cv_to_photo(
                self.puzzle.original_image
            )
        )

        self.original_canvas.create_image(
            0,
            0,
            anchor=tk.NW,
            image=self.original_photo
        )

        if self.hint_home:

            self.draw_circle(
                self.original_canvas,
                *self.hint_home
            )

    # =========================================================
    # PUZZLE IMAGE
    # =========================================================

    def draw_puzzle(self):

        self.puzzle_canvas.delete(
            "all"
        )

        puzzle_image = (
            self.puzzle
            .get_display_image()
        )

        self.puzzle_photo = (
            self.cv_to_photo(
                puzzle_image
            )
        )

        self.puzzle_canvas.create_image(
            0,
            0,
            anchor=tk.NW,
            image=self.puzzle_photo
        )

        self.draw_grid()
        self.draw_correct_ticks()

        if self.selected_tile:

            self.draw_selection()

        if self.hint_current:

            self.draw_circle(
                self.puzzle_canvas,
                *self.hint_current
            )

    # =========================================================
    # GRID
    # =========================================================

    def draw_grid(self):

        size = (
            self.puzzle
            .original_image.shape[0]
        )

        tile_size = (
            size /
            self.puzzle.grid_size
        )

        for i in range(
            1,
            self.puzzle.grid_size
        ):

            position = (
                i * tile_size
            )

            self.puzzle_canvas.create_line(
                position,
                0,
                position,
                size,
                fill="grey"
            )

            self.puzzle_canvas.create_line(
                0,
                position,
                size,
                position,
                fill="grey"
            )

    # =========================================================
    # SELECTION
    # =========================================================

    def draw_selection(self):

        row, col = self.selected_tile

        size = (
            self.puzzle
            .original_image.shape[0]
        )

        tile_size = (
            size /
            self.puzzle.grid_size
        )

        x1 = col * tile_size
        y1 = row * tile_size

        x2 = x1 + tile_size
        y2 = y1 + tile_size

        self.puzzle_canvas.create_rectangle(
            x1 + 2,
            y1 + 2,
            x2 - 2,
            y2 - 2,
            outline="red",
            width=4
        )

    # =========================================================
    # CORRECT TICKS
    # =========================================================

    def draw_correct_ticks(self):

        size = (
            self.puzzle
            .original_image.shape[0]
        )

        tile_size = (
            size /
            self.puzzle.grid_size
        )

        for row in range(
            self.puzzle.grid_size
        ):

            for col in range(
                self.puzzle.grid_size
            ):

                if (
                    self.puzzle
                    .is_tile_correct(
                        row,
                        col
                    )
                ):

                    x = (
                        col * tile_size
                        + tile_size - 18
                    )

                    y = (
                        row * tile_size
                        + 18
                    )

                    self.puzzle_canvas.create_text(
                        x,
                        y,
                        text="✓",
                        fill="green",
                        font=(
                            "Arial",
                            18,
                            "bold"
                        )
                    )

    # =========================================================
    # HINT
    # =========================================================

    def show_hint(self):

        if (
            self.puzzle is None
            or self.hints_remaining <= 0
        ):
            return

        hint = self.puzzle.get_hint()

        if hint is None:
            return

        self.hint_current, self.hint_home = hint

        self.hints_remaining -= 1

        if self.hints_remaining == 0:

            self.hint_button.config(
                state=tk.DISABLED
            )

        self.refresh()

    def draw_circle(
        self,
        canvas,
        row,
        col
    ):

        size = (
            self.puzzle
            .original_image.shape[0]
        )

        tile_size = (
            size /
            self.puzzle.grid_size
        )

        x = (
            col * tile_size
            + tile_size / 2
        )

        y = (
            row * tile_size
            + tile_size / 2
        )

        radius = 20

        canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            outline="blue",
            width=4
        )

    # =========================================================
    # SOLVE
    # =========================================================

    def solve(self):

        if self.puzzle is None:
            return

        self.puzzle.solve()

        self.moves = 0

        self.selected_tile = None

        self.hint_current = None
        self.hint_home = None

        self.game_finished = True

        self.hint_button.config(
            state=tk.DISABLED
        )

        self.solve_button.config(
            state=tk.DISABLED
        )

        self.refresh()

    # =========================================================
    # OPENCV -> TKINTER
    # =========================================================

    @staticmethod
    def cv_to_photo(image):

        rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        pil_image = Image.fromarray(
            rgb
        )

        return ImageTk.PhotoImage(
            pil_image
        )