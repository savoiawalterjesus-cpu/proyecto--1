"""Desktop Match-3 prototype built with Python's standard tkinter library."""

import tkinter as tk
from fractions import Fraction
from pathlib import Path
from tkinter import font

from game_core import Board

CELL_SIZE = 62
CELL_GAP = 6
CELL_STEP = CELL_SIZE + CELL_GAP
BOARD_PADDING = 10
BOARD_PIXELS = BOARD_PADDING * 2 + 8 * CELL_SIZE + 7 * CELL_GAP
TARGET_SCORE = 500
GEM_ASSET_DIR = Path(__file__).resolve().parent / "assets" / "gems"

GEM_COLORS = {
    "gema_1": "#E9575B",
    "gema_2": "#73B96D",
    "gema_3": "#F2A541",
    "gema_4": "#6289D5",
    "gema_5": "#9B68C4",
    "gema_6": "#F2D16B",
}

BACKGROUND = "#F5F3E9"
PANEL = "#FFFDF7"
EMPTY_CELL = "#EDF1E5"
TEXT = "#294735"
MUTED = "#778675"
ACCENT = "#E99545"
LEAF = "#4E8A58"


class Match3App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Match Fruits")
        self.root.configure(bg=BACKGROUND)
        self.root.resizable(False, False)
        self.root.geometry("700x850")
        self.board = Board()
        self.selected: tuple[int, int] | None = None
        self.finished = False
        self.animation_busy = False
        self.animation_job: str | None = None
        self.preview_swap: tuple[tuple[int, int], tuple[int, int]] | None = None
        self.animation_matches: set[tuple[int, int]] = set()
        self.animation_scale = 1.0
        self.swap_progress: float | None = None
        self.gem_images: dict[str, tk.PhotoImage] = {}
        self.gem_animation_images: dict[str, dict[float, tk.PhotoImage]] = {}
        self._load_gem_images()

        self.score_text = tk.StringVar()
        self.moves_text = tk.StringVar()
        self.status_text = tk.StringVar(value="Alinea tres frutas iguales para sumar puntos.")
        self._build_layout()
        self._refresh()

    def _load_gem_images(self) -> None:
        max_dimension = CELL_SIZE - 8
        for gem_id in GEM_COLORS:
            image_path = GEM_ASSET_DIR / f"{gem_id}.png"
            if not image_path.is_file():
                continue
            try:
                image = tk.PhotoImage(master=self.root, file=str(image_path))
            except (tk.TclError, OSError):
                continue

            largest_dimension = max(image.width(), image.height())
            if largest_dimension > max_dimension:
                scale = Fraction(max_dimension, largest_dimension).limit_denominator(8)
                image = image.zoom(scale.numerator, scale.numerator).subsample(
                    scale.denominator, scale.denominator
                )
            self.gem_images[gem_id] = image
            self.gem_animation_images[gem_id] = {
                0.72: image.zoom(3, 3).subsample(4, 4),
                0.4: image.zoom(2, 2).subsample(5, 5),
                0.12: image.subsample(8, 8),
            }

    def _build_layout(self) -> None:
        heading_font = font.Font(family="Georgia", size=28, weight="bold")
        label_font = font.Font(family="Segoe UI", size=9, weight="bold")
        value_font = font.Font(family="Segoe UI", size=20, weight="bold")

        header = tk.Frame(self.root, bg=BACKGROUND)
        header.pack(fill="x", padx=30, pady=(20, 16))
        tk.Label(
            header, text="MATCH FRUITS", font=heading_font, fg=TEXT, bg=BACKGROUND
        ).pack(anchor="center")
        tk.Label(
            header,
            text="DIVERSIÓN FRESCA  /  3 EN LÍNEA",
            font=("Segoe UI", 9, "bold"),
            fg=ACCENT,
            bg=BACKGROUND,
        ).pack(anchor="center", pady=(4, 0))

        stats = tk.Frame(self.root, bg=PANEL, padx=18, pady=12, highlightthickness=1,
                         highlightbackground="#E4E8D9")
        stats.pack(fill="x", padx=55, pady=(0, 14))
        score_box = tk.Frame(stats, bg=PANEL)
        score_box.pack(side="left", expand=True)
        moves_box = tk.Frame(stats, bg=PANEL)
        moves_box.pack(side="right", expand=True)
        tk.Label(score_box, text="PUNTOS", font=label_font, fg=MUTED, bg=PANEL).pack()
        tk.Label(score_box, textvariable=self.score_text, font=value_font, fg=TEXT, bg=PANEL).pack(pady=(2, 0))
        tk.Label(moves_box, text="MOVIMIENTOS", font=label_font, fg=MUTED, bg=PANEL).pack()
        tk.Label(moves_box, textvariable=self.moves_text, font=value_font, fg=ACCENT, bg=PANEL).pack(pady=(2, 0))

        self.canvas = tk.Canvas(
            self.root,
            width=BOARD_PIXELS,
            height=BOARD_PIXELS,
            bg="#E5EBDC",
            highlightthickness=0,
        )
        self.canvas.pack(padx=20, pady=(0, 14))
        self.canvas.bind("<Button-1>", self._on_board_click)

        footer = tk.Frame(self.root, bg=BACKGROUND)
        footer.pack(fill="x", padx=55, pady=(0, 2))
        tk.Label(
            footer,
            text=f"OBJETIVO  /  {TARGET_SCORE} PUNTOS",
            font=label_font,
            fg=TEXT,
            bg=BACKGROUND,
        ).pack(side="left")
        tk.Button(
            footer,
            text="  Nueva partida  ",
            command=self._restart,
            font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF",
            bg=LEAF,
            activebackground="#3D7447",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=8,
            pady=8,
            cursor="hand2",
            bd=0,
        ).pack(side="right")

        tk.Label(
            self.root,
            textvariable=self.status_text,
            font=("Segoe UI", 10, "bold"),
            fg=TEXT,
            bg=BACKGROUND,
            wraplength=600,
            justify="center",
        ).pack(padx=25, pady=(14, 0))

    def _refresh(self) -> None:
        self.score_text.set(f"{self.board.score:04d}")
        self.moves_text.set(str(self.board.moves_left))
        self.canvas.delete("all")
        moving_gems = None
        if self.preview_swap is not None and self.swap_progress is not None:
            first, second = self.preview_swap
            moving_gems = (
                (first, second, self.board.grid[first[0]][first[1]]),
                (second, first, self.board.grid[second[0]][second[1]]),
            )
        for row in range(self.board.size):
            for column in range(self.board.size):
                left = BOARD_PADDING + column * CELL_STEP
                top = BOARD_PADDING + row * CELL_STEP
                right = left + CELL_SIZE
                bottom = top + CELL_SIZE
                selected = self.selected == (row, column)
                self.canvas.create_rectangle(
                    left,
                    top,
                    right,
                    bottom,
                    fill=EMPTY_CELL,
                    outline=ACCENT if selected else "#E1E8DA",
                    width=3 if selected else 1,
                )
                if moving_gems and (row, column) in (first, second):
                    continue
                gem_id = self.board.grid[row][column]
                if self.preview_swap is not None and self.swap_progress is None:
                    first, second = self.preview_swap
                    if (row, column) == first:
                        gem_id = self.board.grid[second[0]][second[1]]
                    elif (row, column) == second:
                        gem_id = self.board.grid[first[0]][first[1]]
                scale = self.animation_scale if (row, column) in self.animation_matches else 1.0
                self._draw_gem(left + CELL_SIZE / 2, top + CELL_SIZE / 2, gem_id, scale)

        if moving_gems:
            progress = self.swap_progress or 0.0
            for start, end, gem_id in moving_gems:
                start_x = BOARD_PADDING + start[1] * CELL_STEP + CELL_SIZE / 2
                start_y = BOARD_PADDING + start[0] * CELL_STEP + CELL_SIZE / 2
                end_x = BOARD_PADDING + end[1] * CELL_STEP + CELL_SIZE / 2
                end_y = BOARD_PADDING + end[0] * CELL_STEP + CELL_SIZE / 2
                center_x = start_x + (end_x - start_x) * progress
                center_y = start_y + (end_y - start_y) * progress
                self._draw_gem(center_x, center_y, gem_id, 1.0)

    def _draw_gem(
        self, center_x: float, center_y: float, gem_id: str, scale: float
    ) -> None:
        image = self.gem_images.get(gem_id)
        if image is not None:
            if scale < 0.3:
                image = self.gem_animation_images[gem_id][0.12]
            elif scale < 0.55:
                image = self.gem_animation_images[gem_id][0.4]
            elif scale < 0.9:
                image = self.gem_animation_images[gem_id][0.72]
            self.canvas.create_image(center_x, center_y, image=image)
            return

        color = GEM_COLORS[gem_id]
        radius = (CELL_SIZE / 2 - 9) * scale
        self.canvas.create_oval(
            center_x - radius + 2,
            center_y - radius + 4,
            center_x + radius + 2,
            center_y + radius + 4,
            fill="#DCE3D6",
            outline="",
        )
        self.canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill=color,
            outline="#FFFFFF",
            width=2,
        )
        if scale < 0.3:
            return
        leaf_scale = min(scale, 1.0)
        self.canvas.create_line(
            center_x,
            center_y - radius + 4,
            center_x + 1,
            center_y - radius - 4,
            fill="#76533B",
            width=max(1, round(2 * leaf_scale)),
        )
        self.canvas.create_oval(
            center_x + 1,
            center_y - radius - 6,
            center_x + 12 * leaf_scale,
            center_y - radius + 1,
            fill=LEAF,
            outline="",
        )

    def _on_board_click(self, event: tk.Event) -> None:
        if self.finished or self.animation_busy:
            return
        column_offset = event.x - BOARD_PADDING
        row_offset = event.y - BOARD_PADDING
        if column_offset < 0 or row_offset < 0:
            return
        column, within_column = divmod(column_offset, CELL_STEP)
        row, within_row = divmod(row_offset, CELL_STEP)
        if (
            row >= self.board.size
            or column >= self.board.size
            or within_row >= CELL_SIZE
            or within_column >= CELL_SIZE
        ):
            return

        clicked = (row, column)
        if self.selected is None:
            self.selected = clicked
            self.status_text.set("Selecciona una fruta vecina para intercambiarla.")
        elif clicked == self.selected:
            self.selected = None
            self.status_text.set("Selección cancelada.")
        elif self._adjacent(self.selected, clicked):
            first, second = self.selected, clicked
            self.selected = None
            matches = self.board.preview_swap(first, second)
            if matches:
                self.preview_swap = (first, second)
                self.animation_matches = matches
                self.animation_busy = True
                self.status_text.set("¡Combinación! Intercambiando frutas...")
                self._animate_swap(0, first, second)
                return
            else:
                self.status_text.set("Ese intercambio no forma una combinación.")
        else:
            self.selected = clicked
            self.status_text.set("Elige una gema vecina a la seleccionada.")
        self._refresh()

    def _animate_swap(
        self, frame: int, first: tuple[int, int], second: tuple[int, int]
    ) -> None:
        frame_count = 8
        if frame >= frame_count:
            self.swap_progress = 1.0
            self._refresh()
            self.animation_job = self.root.after(
                45, lambda: self._begin_destruction(first, second)
            )
            return

        progress = frame / frame_count
        self.swap_progress = progress * progress * (3 - 2 * progress)
        self._refresh()
        self.animation_job = self.root.after(
            25, lambda: self._animate_swap(frame + 1, first, second)
        )

    def _begin_destruction(
        self, first: tuple[int, int], second: tuple[int, int]
    ) -> None:
        self.swap_progress = None
        self.status_text.set("¡Deliciosa combinación! Las frutas desaparecen...")
        self._animate_destruction(0, first, second)

    def _animate_destruction(
        self, frame: int, first: tuple[int, int], second: tuple[int, int]
    ) -> None:
        scales = (1.0, 0.72, 0.4, 0.12)
        if frame == len(scales):
            self.preview_swap = None
            self.animation_matches.clear()
            self.animation_scale = 1.0
            accepted = self.board.play_swap(first, second)
            self.animation_busy = False
            self.animation_job = None
            if accepted:
                self.status_text.set("¡Buena combinación! Sigue buscando líneas.")
                self._check_game_end()
            else:
                self.status_text.set("No se pudo completar el intercambio.")
            self._refresh()
            return

        self.animation_scale = scales[frame]
        self._refresh()
        self.animation_job = self.root.after(
            85, lambda: self._animate_destruction(frame + 1, first, second)
        )

    @staticmethod
    def _adjacent(first: tuple[int, int], second: tuple[int, int]) -> bool:
        return abs(first[0] - second[0]) + abs(first[1] - second[1]) == 1

    def _check_game_end(self) -> None:
        if self.board.moves_left == 0:
            self.finished = True
            if self.board.score >= TARGET_SCORE:
                self.status_text.set(
                    "Fin de la partida. ¡Objetivo alcanzado! Inicia otra para volver a jugar."
                )
            else:
                self.status_text.set("Fin de la partida. Inicia otra para intentarlo de nuevo.")
        elif self.board.score >= TARGET_SCORE:
            self.status_text.set(
                "¡Objetivo alcanzado! Puedes seguir jugando o iniciar otra partida."
            )

    def _restart(self) -> None:
        if self.animation_job is not None:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None
        self.animation_busy = False
        self.preview_swap = None
        self.swap_progress = None
        self.animation_matches.clear()
        self.animation_scale = 1.0
        self.board.reset()
        self.selected = None
        self.finished = False
        self.status_text.set("Alinea tres frutas iguales para sumar puntos.")
        self._refresh()


def main() -> None:
    root = tk.Tk()
    Match3App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
