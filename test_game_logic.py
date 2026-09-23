import unittest

from game_logic import PuzzleGame, Tile


class TestTile(unittest.TestCase):
    """Tests for individual puzzle tiles."""

    def test_new_tile_is_correct(self):
        tile = Tile(0, 0)

        self.assertTrue(tile.is_correct())
        self.assertEqual(tile.rotation, 0)
        self.assertFalse(tile.flipped)

    def test_tile_rotation(self):
        tile = Tile(0, 0)

        tile.rotate_clockwise()
        self.assertEqual(tile.rotation, 90)
        self.assertFalse(tile.is_correct())

        tile.rotate_clockwise()
        tile.rotate_clockwise()
        tile.rotate_clockwise()

        self.assertEqual(tile.rotation, 0)
        self.assertTrue(tile.is_correct())

    def test_tile_flip(self):
        tile = Tile(0, 0)

        tile.flip_horizontal()
        self.assertTrue(tile.flipped)
        self.assertFalse(tile.is_correct())

        tile.flip_horizontal()
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

    def test_invalid_grid_size(self):
        with self.assertRaises(ValueError):
            PuzzleGame(6)

    def test_select_and_swap(self):
        game = PuzzleGame(3)

        game.select_or_swap(0)
        self.assertEqual(game.selected_position, 0)

        game.select_or_swap(1)

        self.assertEqual(game.tiles[0].tile_id, 1)
        self.assertEqual(game.tiles[1].tile_id, 0)
        self.assertEqual(game.moves, 1)
        self.assertIsNone(game.selected_position)

    def test_rotate_and_flip_count_as_moves(self):
        game = PuzzleGame(3)

        game.rotate_tile(0)
        self.assertEqual(game.tiles[0].rotation, 90)
        self.assertEqual(game.moves, 1)

        game.flip_tile(1)
        self.assertTrue(game.tiles[1].flipped)
        self.assertEqual(game.moves, 2)

    def test_hint_limit(self):
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

        game.solve()

        self.assertTrue(game.is_complete())
        self.assertTrue(game.game_complete)
        self.assertEqual(game.tiles_left(), 0)
        self.assertEqual(game.moves, 0)


if __name__ == "__main__":
    unittest.main()
