"""Match-3 board rules, kept independent from the graphical interface."""

from __future__ import annotations

import random
from collections.abc import Iterable

GEM_TYPES = tuple(f"gema_{number}" for number in range(1, 7))
Position = tuple[int, int]


class Board:
    def __init__(
        self,
        size: int = 8,
        gem_types: Iterable[str] = GEM_TYPES,
        rng: random.Random | None = None,
    ) -> None:
        self.size = size
        self.gem_types = tuple(gem_types)
        if self.size < 3:
            raise ValueError("El tablero debe tener al menos 3 filas y columnas.")
        if len(self.gem_types) < 3:
            raise ValueError("Se necesitan al menos 3 tipos de gema.")
        self.rng = rng or random.Random()
        self.score = 0
        self.moves_left = 25
        self.grid: list[list[str]] = []
        self.reset()

    def reset(self) -> None:
        self.score = 0
        self.moves_left = 25
        self.grid = self._new_grid()
        while not self.has_possible_move():
            self.grid = self._new_grid()

    def _new_grid(self) -> list[list[str]]:
        grid: list[list[str]] = []
        for row in range(self.size):
            line: list[str] = []
            for column in range(self.size):
                choices = list(self.gem_types)
                if column >= 2 and line[-1] == line[-2]:
                    choices = [gem for gem in choices if gem != line[-1]]
                if row >= 2 and grid[row - 1][column] == grid[row - 2][column]:
                    choices = [gem for gem in choices if gem != grid[row - 1][column]]
                line.append(self.rng.choice(choices))
            grid.append(line)
        return grid

    def find_matches(self) -> set[Position]:
        matches: set[Position] = set()
        for row in range(self.size):
            for column in range(self.size - 2):
                gem = self.grid[row][column]
                if gem == self.grid[row][column + 1] == self.grid[row][column + 2]:
                    end = column + 3
                    while end < self.size and self.grid[row][end] == gem:
                        end += 1
                    matches.update((row, index) for index in range(column, end))
        for column in range(self.size):
            for row in range(self.size - 2):
                gem = self.grid[row][column]
                if gem == self.grid[row + 1][column] == self.grid[row + 2][column]:
                    end = row + 3
                    while end < self.size and self.grid[end][column] == gem:
                        end += 1
                    matches.update((index, column) for index in range(row, end))
        return matches

    def play_swap(self, first: Position, second: Position) -> bool:
        if self.moves_left <= 0 or not self._are_adjacent(first, second):
            return False
        self._swap(first, second)
        if not self.find_matches():
            self._swap(first, second)
            return False

        self.moves_left -= 1
        cascade = 0
        matches = self.find_matches()
        while matches:
            cascade += 1
            self.score += len(matches) * 10 * cascade
            for row, column in matches:
                self.grid[row][column] = ""
            self._drop_and_refill()
            matches = self.find_matches()

        if not self.has_possible_move():
            self._reshuffle()
        return True

    def preview_swap(self, first: Position, second: Position) -> set[Position]:
        if self.moves_left <= 0 or not self._are_adjacent(first, second):
            return set()
        self._swap(first, second)
        matches = self.find_matches()
        self._swap(first, second)
        return matches

    def has_possible_move(self) -> bool:
        for row in range(self.size):
            for column in range(self.size):
                for neighbor in ((row, column + 1), (row + 1, column)):
                    if neighbor[0] >= self.size or neighbor[1] >= self.size:
                        continue
                    self._swap((row, column), neighbor)
                    makes_match = bool(self.find_matches())
                    self._swap((row, column), neighbor)
                    if makes_match:
                        return True
        return False

    def _drop_and_refill(self) -> None:
        for column in range(self.size):
            remaining = [
                self.grid[row][column]
                for row in range(self.size)
                if self.grid[row][column]
            ]
            new_gems = [self.rng.choice(self.gem_types) for _ in range(self.size - len(remaining))]
            values = new_gems + remaining
            for row, gem in enumerate(values):
                self.grid[row][column] = gem

    def _reshuffle(self) -> None:
        self.grid = self._new_grid()
        while not self.has_possible_move():
            self.grid = self._new_grid()

    def _are_adjacent(self, first: Position, second: Position) -> bool:
        return (
            0 <= first[0] < self.size
            and 0 <= first[1] < self.size
            and 0 <= second[0] < self.size
            and 0 <= second[1] < self.size
            and abs(first[0] - second[0]) + abs(first[1] - second[1]) == 1
        )

    def _swap(self, first: Position, second: Position) -> None:
        first_row, first_column = first
        second_row, second_column = second
        self.grid[first_row][first_column], self.grid[second_row][second_column] = (
            self.grid[second_row][second_column],
            self.grid[first_row][first_column],
        )
