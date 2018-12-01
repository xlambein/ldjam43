import pyxel
import numpy as np


PLAYER_SPEED = 2
PLAYER_JUMP = 3
GRAVITY = .4


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = 0
        self.w = 8
        self.h = 8

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= PLAYER_SPEED

        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += PLAYER_SPEED

        # Physics
        self.y += self.vy

        # Collisions
        bottom = self.col_bottom()
        if bottom == False:
            # Gravity
            self.vy += GRAVITY
        else:
            self.vy = 0
            self.y = bottom

            if pyxel.btn(pyxel.KEY_UP):
                self.vy = -PLAYER_JUMP

    def col_bottom(self):
        # FIXME assumes the player is not larger than a tile
        bottom = [
            (self.x//8,            (self.y+self.h)//8),
            ((self.x+self.w-1)//8, (self.y+self.h)//8)
        ]
        for (x, y) in bottom:
            if pyxel.tilemap(0).get(int(x), int(y)) != 0:
                return y * 8 - self.h
        return False

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 8, 0, self.h, self.w, 0)


class App:
    def __init__(self):
        pyxel.init(16*8, 16*8,
            caption="Sacrifices Must be Made",
            fps=30,
            scale=8)

        pyxel.load("resource.pyxel")

        py, px = np.where(pyxel.tilemap(0).data[:16,:16] == 1)
        px, py = px[0], py[0]
        self.player = Player(px * 8, py * 8)

        pyxel.tilemap(0).set(px, py, 2)

        pyxel.run(self.update, self.draw)

    def update(self):
        self.player.update()

    def draw(self):
        pyxel.cls(0)
        pyxel.bltm(0, 0, 0, 0, 0, 16, 16)

        self.player.draw()

App()

