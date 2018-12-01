import pyxel
import numpy as np


FPS = 60
PLAYER_SPEED = 60/FPS
PLAYER_JUMP = 150/FPS
GRAVITY = 12/FPS


def is_wall(x, y):
    return pyxel.tilemap(0).get(x, y) != 0


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = 0
        self.w = 4
        self.h = 8

    def update(self):
        # Physics
        self.y += self.vy

        # Collisions
        top = self.col_top()
        if top != False:
            self.vy = max(0, self.vy)
            self.y = top

        bottom = self.col_bottom()
        if bottom == False:
            # Gravity
            self.vy += GRAVITY
        else:
            self.vy = max(0, self.vy)
            self.y = bottom - self.h

            if pyxel.btn(pyxel.KEY_UP):
                self.vy = -PLAYER_JUMP

        left = self.col_left()
        if left != False:
            self.x = left
        else:
            if pyxel.btn(pyxel.KEY_LEFT):
                self.x -= PLAYER_SPEED

        right = self.col_right()
        if right != False:
            self.x = right - self.w
        else:
            if pyxel.btn(pyxel.KEY_RIGHT):
                self.x += PLAYER_SPEED

    def col_left(self):
        x = int((self.x-1)//8)
        f, t = int(self.y//8), int((self.y+self.h-1)//8)
        for y in range(f, t+1):
            if is_wall(x, y):
                return (x+1) * 8
        return False

    def col_right(self):
        x = int((self.x+self.w)//8)
        f, t = int(self.y//8), int((self.y+self.h-1)//8)
        for y in range(f, t+1):
            if is_wall(x, y):
                return x * 8
        return False

    def col_top(self):
        y = int((self.y-1)//8)
        f, t = int(self.x//8), int((self.x+self.w-1)//8)
        for x in range(f, t+1):
            if is_wall(x, y):
                return (y+1) * 8
        return False

    def col_bottom(self):
        y = int((self.y+self.h)//8)
        f, t = int(self.x//8), int((self.x+self.w-1)//8)
        for x in range(f, t+1):
            if is_wall(x, y):
                return y * 8
        return False

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 10, 0, self.w, self.h, 0)


class App:
    def __init__(self):
        pyxel.init(16*8, 16*8,
            caption="Sacrifices Must be Made",
            fps=FPS,
            scale=8)

        pyxel.load("resource.pyxel")

        py, px = np.where(pyxel.tilemap(0).data[:16,:16] == 1)
        px, py = px[0], py[0]
        self.player = Player(px * 8, py * 8)

        pyxel.tilemap(0).set(px, py, 0)

        pyxel.run(self.update, self.draw)

    def update(self):
        self.player.update()

    def draw(self):
        pyxel.cls(0)
        pyxel.bltm(0, 0, 0, 0, 0, 16, 16)

        self.player.draw()

App()

