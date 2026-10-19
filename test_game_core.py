import random
import unittest

from game_core import Board, GEM_TYPES


class BoardTests(unittest.TestCase):
    def test_new_board_has_no_matches_and_has_a_move(self):
        board = Board(rng=random.Random(7))

        self.assertEqual(board.find_matches(), set())
        self.assertTrue(board.has_possible_move())

    def test_only_a_matching_adjacent_swap_consumes_a_move(self):
        board = Board(rng=random.Random(11))
        board.grid = [
            [GEM_TYPES[(row + column) % len(GEM_TYPES)] for column in range(board.size)]
            for row in range(board.size)
        ]
        board.grid[0][2] = GEM_TYPES[0]
        board.grid[1][1] = GEM_TYPES[0]

        self.assertFalse(board.play_swap((0, 0), (7, 7)))
        self.assertEqual(board.moves_left, 25)
        self.assertTrue(board.play_swap((0, 1), (1, 1)))
        self.assertEqual(board.moves_left, 24)
        self.assertGreaterEqual(board.score, 30)
        self.assertEqual(board.find_matches(), set())

    def test_swap_without_a_match_is_reverted(self):
        board = Board(rng=random.Random(21))
        original = [row[:] for row in board.grid]
        rejected_swap = None
        for row in range(board.size):
            for column in range(board.size - 1):
                board._swap((row, column), (row, column + 1))
                makes_match = bool(board.find_matches())
                board._swap((row, column), (row, column + 1))
                if not makes_match:
                    rejected_swap = ((row, column), (row, column + 1))
                    break
            if rejected_swap:
                break

        self.assertIsNotNone(rejected_swap)
        first, second = rejected_swap
        self.assertFalse(board.play_swap(first, second))
        self.assertEqual(board.grid, original)
        self.assertEqual(board.moves_left, 25)

    def test_preview_finds_match_without_changing_board(self):
        board = Board(rng=random.Random(31))
        board.grid = [
            [GEM_TYPES[(row + column) % len(GEM_TYPES)] for column in range(board.size)]
            for row in range(board.size)
        ]
        board.grid[0][2] = GEM_TYPES[0]
        board.grid[1][1] = GEM_TYPES[0]
        original = [row[:] for row in board.grid]

        matches = board.preview_swap((0, 1), (1, 1))

        self.assertEqual(matches, {(0, 0), (0, 1), (0, 2)})
        self.assertEqual(board.grid, original)
        self.assertEqual(board.moves_left, 25)


if __name__ == "__main__":
    unittest.main()
