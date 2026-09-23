import unittest

from game_logic import (
    PuzzleAction,
    SwapAction,
    RotateAction,
    FlipAction,
    Tile,
    PuzzleGame,
)


class TestTile(unittest.TestCase):
    """Tests for individual puzzle tiles."""

    def test_new_tile_state(self):
        tile = Tile(0, 0)

        self.assertEqual(tile.tile_id, 0)
        self.assertEqual(tile.correct_position, 0)
        self.assertEqual(tile.current_position, 0)
        self.assertEqual(tile.rotation, 0)
        self.assertFalse(tile.flipped)
        self.assertTrue(tile.is_correct())

    def test_rotation(self):
        tile = Tile(0, 0)

        tile.rotate_clockwise()
        self.assertEqual(tile.rotation, 90)
        self.assertFalse(tile.is_correct())

        tile.rotate_clockwise()
        tile.rotate_clockwise()
        tile.rotate_clockwise()

        self.assertEqual(tile.rotation, 0)
        self.assertTrue(tile.is_correct())

    def test_horizontal_flip(self):
        tile = Tile(0, 0)

        tile.flip_horizontal()

        self.assertTrue(tile.flipped)
        self.assertFalse(tile.is_correct())

        tile.flip_horizontal()

        self.assertFalse(tile.flipped)
        self.assertTrue(tile.is_correct())

    def test_reset_orientation(self):
        tile = Tile(0, 0)

        tile.rotate_clockwise()
        tile.flip_horizontal()

        tile.reset_orientation()

        self.assertEqual(tile.rotation, 0)
        self.assertFalse(tile.flipped)
        self.assertTrue(tile.is_correct())


class TestPuzzleGame(unittest.TestCase):
    """Tests for the main puzzle game logic."""

    def test_supported_grid_sizes(self):
        expected_tiles = {
            3: 9,
            4: 16,
            5: 25,
        }

        for grid_size, tile_count in expected_tiles.items():
            game = PuzzleGame(grid_size)

            self.assertEqual(game.grid_size, grid_size)
            self.assertEqual(len(game.tiles), tile_count)
            self.assertEqual(game.moves, 0)
            self.assertEqual(game.hints_used, 0)

    def test_invalid_grid_size(self):
        with self.assertRaises(ValueError):
            PuzzleGame(2)

        with self.assertRaises(ValueError):
            PuzzleGame(6)

    def test_invalid_tile_position(self):
        game = PuzzleGame(3)

        with self.assertRaises(IndexError):
            game.rotate_tile(9)

        with self.assertRaises(IndexError):
            game.flip_tile(-1)

        with self.assertRaises(TypeError):
            game.rotate_tile("0")

    def test_select_tile(self):
        game = PuzzleGame(3)

        result = game.select_or_swap(0)

        self.assertFalse(result)
        self.assertEqual(game.selected_position, 0)
        self.assertEqual(game.moves, 0)

    def test_select_same_tile_deselects(self):
        game = PuzzleGame(3)

        game.select_or_swap(0)
        game.select_or_swap(0)

        self.assertIsNone(game.selected_position)
        self.assertEqual(game.moves, 0)

    def test_swap_tiles(self):
        game = PuzzleGame(3)

        game.select_or_swap(0)
        result = game.select_or_swap(1)

        self.assertTrue(result)
        self.assertEqual(game.tiles[0].tile_id, 1)
        self.assertEqual(game.tiles[1].tile_id, 0)
        self.assertEqual(game.tiles[0].current_position, 0)
        self.assertEqual(game.tiles[1].current_position, 1)
        self.assertEqual(game.moves, 1)
        self.assertIsNone(game.selected_position)
        self.assertEqual(game.tiles_left(), 2)

    def test_player_rotation_counts_move(self):
        game = PuzzleGame(3)

        result = game.rotate_tile(0)

        self.assertTrue(result)
        self.assertEqual(game.tiles[0].rotation, 90)
        self.assertEqual(game.moves, 1)
        self.assertEqual(game.tiles_left(), 1)

    def test_player_flip_counts_move(self):
        game = PuzzleGame(3)

        result = game.flip_tile(0)

        self.assertTrue(result)
        self.assertTrue(game.tiles[0].flipped)
        self.assertEqual(game.moves, 1)
        self.assertEqual(game.tiles_left(), 1)

    def test_tiles_left(self):
        game = PuzzleGame(3)

        self.assertEqual(game.tiles_left(), 0)

        game.rotate_tile(0)
        self.assertEqual(game.tiles_left(), 1)

        game.flip_tile(1)
        self.assertEqual(game.tiles_left(), 2)

    def test_hint_identifies_incorrect_tile(self):
        game = PuzzleGame(3)

        game.rotate_tile(4)

        hint = game.request_hint()

        self.assertEqual(hint, (4, 4))
        self.assertEqual(game.active_hint, (4, 4))
        self.assertEqual(game.hints_used, 1)
        self.assertEqual(game.hints_remaining(), 2)

    def test_hint_clears_after_next_move(self):
        game = PuzzleGame(3)

        game.rotate_tile(0)
        game.request_hint()

        self.assertIsNotNone(game.active_hint)

        game.rotate_tile(1)

        self.assertIsNone(game.active_hint)

    def test_three_hint_limit(self):
        game = PuzzleGame(3)

        game.rotate_tile(0)

        self.assertIsNotNone(game.request_hint())
        self.assertIsNotNone(game.request_hint())
        self.assertIsNotNone(game.request_hint())

        self.assertEqual(game.hints_used, 3)
        self.assertEqual(game.hints_remaining(), 0)
        self.assertIsNone(game.request_hint())

    def test_solve_restores_puzzle(self):
        game = PuzzleGame(3)

        game.select_or_swap(0)
        game.select_or_swap(1)
        game.rotate_tile(2)
        game.flip_tile(3)

        self.assertGreater(game.tiles_left(), 0)
        self.assertGreater(game.moves, 0)

        game.solve()

        self.assertTrue(game.is_complete())
        self.assertTrue(game.game_complete)
        self.assertEqual(game.tiles_left(), 0)
        self.assertEqual(game.moves, 0)
        self.assertIsNone(game.selected_position)
        self.assertIsNone(game.active_hint)

        for position, tile in enumerate(game.tiles):
            self.assertEqual(tile.current_position, position)
            self.assertEqual(tile.correct_position, position)
            self.assertEqual(tile.rotation, 0)
            self.assertFalse(tile.flipped)

    def test_completed_game_locks_player_input(self):
        game = PuzzleGame(3)

        game.rotate_tile(0)
        game.solve()

        moves_before = game.moves

        self.assertFalse(game.rotate_tile(0))
        self.assertFalse(game.flip_tile(0))
        self.assertFalse(game.select_or_swap(0))

        self.assertEqual(game.moves, moves_before)

    def test_reset_game(self):
        game = PuzzleGame(4)

        game.rotate_tile(0)
        game.request_hint()

        game.reset_game()

        self.assertEqual(game.grid_size, 4)
        self.assertEqual(len(game.tiles), 16)
        self.assertEqual(game.moves, 0)
        self.assertEqual(game.hints_used, 0)
        self.assertIsNone(game.active_hint)
        self.assertFalse(game.game_complete)
        self.assertEqual(game.tiles_left(), 0)


class TestPuzzleActions(unittest.TestCase):
    """Tests for inheritance and polymorphic puzzle actions."""

    def test_action_inheritance(self):
        self.assertTrue(issubclass(SwapAction, PuzzleAction))
        self.assertTrue(issubclass(RotateAction, PuzzleAction))
        self.assertTrue(issubclass(FlipAction, PuzzleAction))

    def test_base_action_requires_implementation(self):
        game = PuzzleGame(3)

        with self.assertRaises(NotImplementedError):
            PuzzleAction().apply(game)

    def test_polymorphic_actions(self):
        game = PuzzleGame(3)

        actions = [
            SwapAction(0, 1),
            RotateAction(2),
            FlipAction(3),
        ]

        for action in actions:
            game.apply_action(action)

        self.assertEqual(game.tiles[0].tile_id, 1)
        self.assertEqual(game.tiles[1].tile_id, 0)
        self.assertEqual(game.tiles[2].rotation, 90)
        self.assertTrue(game.tiles[3].flipped)

        # Setup transformations must not count as player moves.
        self.assertEqual(game.moves, 0)
        self.assertEqual(game.tiles_left(), 4)

    def test_invalid_action_rejected(self):
        game = PuzzleGame(3)

        with self.assertRaises(TypeError):
            game.apply_action("rotate")


if __name__ == "__main__":
    unittest.main()
