import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from main import Match3App


class Match3AppTests(unittest.TestCase):
    def test_reaching_target_keeps_board_playable_while_moves_remain(self):
        app = Match3App.__new__(Match3App)
        app.board = SimpleNamespace(score=580, moves_left=17)
        app.finished = False
        app.status_text = Mock()

        app._check_game_end()

        self.assertFalse(app.finished)
        app.status_text.set.assert_called_once_with(
            "¡Objetivo alcanzado! Puedes seguir jugando o iniciar otra partida."
        )

    def test_zero_moves_ends_game_even_after_reaching_target(self):
        app = Match3App.__new__(Match3App)
        app.board = SimpleNamespace(score=580, moves_left=0)
        app.finished = False
        app.status_text = Mock()

        app._check_game_end()

        self.assertTrue(app.finished)
        app.status_text.set.assert_called_once_with(
            "Fin de la partida. ¡Objetivo alcanzado! Inicia otra para volver a jugar."
        )


if __name__ == "__main__":
    unittest.main()
