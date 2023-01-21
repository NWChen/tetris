#from abc import ABC
from datetime import datetime
import os
import random
import select
import sys

class Piece():
    def __init__(self, bodies):
        self.rot_idx = 0
        self.bodies = bodies
        self.body = self.bodies[self.rot_idx]

    def get_weight(self):
        return max(tup[1] for tup in self.body) - min(tup[1] for tup in self.body)

    def get_width(self):
        return max(tup[0] for tup in self.body) - min(tup[0] for tup in self.body)

    def rotate(self):
        self.rot_idx = (self.rot_idx + 1) % len(self.bodies)
        self.body = self.bodies[self.rot_idx]
        return self.body


T_BODIES = [
    [(0, 0), (1, 0), (1, 1), (2, 0)],
    [(0, 0), (0, 1), (0, 2), (1, 1)],
    [(0, 1), (1, 1), (2, 1), (1, 0)],
    [(0, 1), (1, 0), (1, 1), (1, 2)],
]

I_BODIES = [
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    [(0, 0), (1, 0), (2, 0), (3, 0)],
]

L_BODIES = [
    [(0, 0), (0, 1), (0, 2), (1, 0)],
    [(0, 0), (0, 1), (1, 1), (2, 1)],
    [(0, 2), (1, 2), (1, 1), (1, 0)],
    [(0, 0), (1, 0), (2, 0), (2, 1)],
]

SQUARE_BODIES = [
    [(0, 0), (0, 1), (1, 0), (1, 1)]
]

# TODO: INV_L, ZIG, ZAG

class Grid():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[False for _ in range(self.width)] for _ in range(self.height)]
    
    def get(self, x, y):
        return self.grid[x][y]

    def clear_filled(self):
        nonempty_rows = [
            row for row in self.grid if not all(row)
        ]
        n_empty_rows = self.height - len(nonempty_rows)
        self.grid = [
            [False for _ in range(self.width)]
            for _ in range(n_empty_rows)
        ] + nonempty_rows

class Game():
    def __init__(self):
        self.WIDTH = 10
        self.HEIGHT = 10
        self.DROP_INTERVAL = 100

        self.step = 0
        self.grid = Grid(self.WIDTH, self.HEIGHT)
        self.pieces = [T_BODIES, I_BODIES, L_BODIES, SQUARE_BODIES]
        self.piece = self.get_next_piece()
        self.row = 0 # bottom-left corner
        self.col = self.WIDTH // 2 # bottom-left corner
        self.t_start = datetime.now()

    def commit(self):
        for (drow, dcol) in self.piece.body:
            row = self.row + drow
            col = self.col + dcol
            self.grid.grid[row][col] = True

    def get_next_piece(self):
        idx = random.randint(0, len(self.pieces) - 1)
        return Piece(self.pieces[idx])

    def get_move(self):
        # ↑ 24 ↓ 25 → 26 ← 27
        m = {
            "\033[A": 'up',
            "\033[B": 'down',
            "\033[D": 'left',
            "\033[C": 'right',
        }
        while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            if line and line.strip() in m:
                return m[line.strip()]
            return 0

    def update(self):
        move = self.get_move()
        if move == 'up':
            self.piece.rotate()
        if move == 'left':
            self.col -= 1
        if move == 'right':
            self.col += 1

        if self.step % self.DROP_INTERVAL == 0:
            self.step = 0
            if self.collides():
                self.commit()
                self.grid.clear_filled()
                self.piece = self.get_next_piece()
                self.row = 0
                self.col = self.WIDTH // 2
            else:
                self.row += 1
        self.step += 1

    def render(self):
        os.system('clear')
        grid = [row[:] for row in self.grid.grid]
        for (drow, dcol) in self.piece.body:
            row = self.row + drow
            col = self.col + dcol
            grid[row][col] = True
            print(row, col)

        t_ms = int((datetime.now() - self.t_start).seconds)
        print(t_ms)
        for row in grid:
            s = ['x' if filled else '.' for filled in row]
            print(''.join(s))
        
    def collides(self):
        for (drow, dcol) in self.piece.body:
            row = self.row + drow
            col = self.col + dcol
            if row + 1 == self.HEIGHT or self.grid.get(row + 1, col):
                return True
        return False

if __name__ == '__main__':
    game = Game()
    while True:
        game.update()
        game.render()
