import pyxel
import numpy as np
from functools import reduce


FPS = 60
PLAYER_SPEED = 60/FPS
PLAYER_JUMP = 150/FPS
GRAVITY = 12/FPS

TEXT_COL = 1
TEXT_WIDTH = 4
TEXT_HEIGHT = 6

GAME_TILES_W = 16
GAME_TILES_H = 16

features = {
    'sprites': True,
    'rendering': True,
    'collisions': True,
    'gravity': True,
    'physics': True,
    'plateforms': True,
    'player': True,
    'enemies': True,
    'music': True,
    'sounds': True,
    'jump': True,
    'left': True,
    'right': True,
    'attack': True,
    'game': True,
    'binary': True,
}

features_name = {
    'sprites': 'Sprites',
    'rendering': 'Rendering',
    'collisions': 'Collisions',
    'gravity': 'Gravity',
    'physics': 'Physics',
    'plateforms': 'Plateforms',
    'player': 'Player',
    'enemies': 'Enemies',
    'music': 'Music',
    'sounds': 'Sounds',
    'jump': 'Jumping',
    'left': 'Moving left',
    'right': 'Moving right',
    'attack': 'Attacking',
    'game': 'Game',
    'binary': 'Game binary',
}


def is_wall(x, y):
    return pyxel.tilemap(0).get(x, y) != 0


class Player:
    def __init__(self, x, y):
        self.w = 4
        self.h = 8
        self.x = x + (8-self.w)//2
        self.y = y
        self.vy = 0

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
        if features['collisions']:
            x = int((self.x-1)//8)
            f, t = int(self.y//8), int((self.y+self.h-1)//8)
            for y in range(f, t+1):
                if is_wall(x, y):
                    return (x+1) * 8
        return False

    def col_right(self):
        if features['collisions']:
            x = int((self.x+self.w)//8)
            f, t = int(self.y//8), int((self.y+self.h-1)//8)
            for y in range(f, t+1):
                if is_wall(x, y):
                    return x * 8
        return False

    def col_top(self):
        if features['collisions']:
            y = int((self.y-1)//8)
            f, t = int(self.x//8), int((self.x+self.w-1)//8)
            for x in range(f, t+1):
                if is_wall(x, y):
                    return (y+1) * 8
        return False

    def col_bottom(self):
        if features['collisions']:
            y = int((self.y+self.h)//8)
            f, t = int(self.x//8), int((self.x+self.w-1)//8)
            for x in range(f, t+1):
                if is_wall(x, y):
                    return y * 8
        return False

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 10, 0, self.w, self.h, 0)


class Menu:
    def __init__(self, title, items):
        self.title = title
        self.items = items
        self.selected = 0

    def update(self):
        if pyxel.btnp(pyxel.KEY_UP, 0.5 * FPS, 0.1 * FPS):
            self.selected = max(self.selected - 1, 0)

        if pyxel.btnp(pyxel.KEY_DOWN, 0.5 * FPS, 0.1 * FPS):
            self.selected = min(self.selected + 1, len(self.items)-1)

        if pyxel.btn(pyxel.KEY_ENTER):
            return self.selected

        return False

    def draw(self):
        text = self.title + '\n\n'

        for i, item in enumerate(self.items):
            if i == self.selected:
                text += '> ' + item + '\n'
            else:
                text += ' ' + item + '\n'

        draw_textbox(text[:-1])

    def get(self, i):
        return self.items[i]


class Scene:
    def update(self):
        return False, None

    def draw(self):
        pass


class LevelScene(Scene):
    def __init__(self):
        py, px = np.where(pyxel.tilemap(0).data[:16,:16] == 1)
        px, py = px[0], py[0]
        self.player = Player(px * 8, py * 8)

        pyxel.tilemap(0).set(px, py, 0)

    def update(self):
        if features['player']:
            self.player.update()

        return False, None

    def draw(self):
        if features['rendering']:
            pyxel.bltm(0, 0, 0, 0, 0, 16, 16)

            if features['player']:
                self.player.draw()


class SacrificeMenuScene(Scene):
    def __init__(self):
        items = [name for name, state in features.items() if state]
        self.menu = Menu("Choose what to sacrifice:", items)

    def update(self):
        selected = self.menu.update()
        if selected != False:
            print("Sacrificed", selected, self.menu.get(selected))
            features[self.menu.get(selected)] = False
            return True, None

        return False, None

    def draw(self):
        if features['rendering']:
            self.menu.draw()


def draw_textbox(text, w=None, h=None):
    lines = text.split('\n')
    lens = map(len, lines)

    cols = reduce(max, lens)
    rows = len(lines)

    if w is None:
        w = int(np.ceil(cols * TEXT_WIDTH / 8))
    if h is None:
        h = int(np.ceil(rows * TEXT_HEIGHT / 8))

    TSX = 1
    TSY = 3

    x = (GAME_TILES_W - w) // 2
    y = (GAME_TILES_H - h) // 2

    pyxel.blt((x-1)*8, (y-1)*8, 0, (TSX-1)*8, (TSY-1)*8, 8, 8, colkey=0)
    pyxel.blt((x+w)*8, (y-1)*8, 0, (TSX+1)*8, (TSY-1)*8, 8, 8, colkey=0)
    pyxel.blt((x-1)*8, (y+h)*8, 0, (TSX-1)*8, (TSY+1)*8, 8, 8, colkey=0)
    pyxel.blt((x+w)*8, (y+h)*8, 0, (TSX+1)*8, (TSY+1)*8, 8, 8, colkey=0)

    for i in range(w):
        pyxel.blt((x+i)*8, (y-1)*8, 0, TSX*8, (TSY-1)*8, 8, 8, colkey=0)
        pyxel.blt((x+i)*8, (y+h)*8, 0, TSX*8, (TSY+1)*8, 8, 8, colkey=0)

    for j in range(h):
        pyxel.blt((x-1)*8, (y+j)*8, 0, (TSX-1)*8, TSY*8, 8, 8, colkey=0)
        pyxel.blt((x+w)*8, (y+j)*8, 0, (TSX+1)*8, TSY*8, 8, 8, colkey=0)

    for i in range(w):
        for j in range(h):
            pyxel.blt((x+i)*8, (y+j)*8, 0, TSX*8, TSY*8, 8, 8)

    pyxel.text(x*8, y*8, text, TEXT_COL)


class App:
    def __init__(self):
        pyxel.init(GAME_TILES_W*8, GAME_TILES_H*8,
            caption="Sacrifices Must be Made",
            fps=FPS,
            scale=8)

        pyxel.load("resource.pyxel")

        self.scene_stack = [
            LevelScene(),
            SacrificeMenuScene()
        ]

        pyxel.run(self.update, self.draw)

    def update(self):
        pop_scene, new_scene = self.scene_stack[-1].update()

        if pop_scene:
            self.scene_stack.pop()
        if new_scene:
            self.scene_stack.append(new_scene)

        if len(self.scene_stack) == 0:
            pyxel.quit()


    def draw(self):
        pyxel.cls(0)
        
        if features['rendering']:
            for scene in self.scene_stack:
                scene.draw()


App()

