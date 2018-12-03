import pyxel
import numpy as np
from functools import reduce


FPS = 60
PLAYER_SPEED = 60/FPS
PLAYER_JUMP = 150/FPS
GRAVITY = 12/FPS

FRICTION_GROUND = 30/FPS
FRICTION_AIR = .95/FPS

TEXT_COL = 1
TEXT_WIDTH = 4
TEXT_HEIGHT = 6

GAME_TILES_W = 16
GAME_TILES_H = 16

FIRST_LEVEL = 0
LAST_LEVEL = 10

TILE_PLAYER = 1
TILE_BLOCK = 32
TILE_DOOR = 33
TILE_CACTUS = 34
TILE_LOCK = 35
TILE_KEY = 36
TILE_UNLOCKED = 37

features = {
    'animations': True,
    'windows': True,
    'sprites': True,

    'keys': True,
    'locks': True,
    'jump': True,
    'gravity': False,
    'friction': False,
    'left': True,

    'tutorial': True,

    'collisions': True,
    'player': True,
    'right': True,
    'rendering': True,
    'game': True,
}

sacrifices = []
last_sacrifice = ''

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
    'friction': 'Friction',
    'locks': 'Locked blocks',
    'keys': 'Keys',
    'tutorial': 'Help text',
    'windows': 'Windows',
    'animations': 'Animations',
}


class GameError(Exception):
    """game errors"""


def is_tile_wall(tile):
    return tile in (TILE_BLOCK, TILE_LOCK)


def is_wall(x, y):
    return is_tile_wall(pyxel.tilemap(0).get(x, y))


def apply_friction(v, amount):
    if v > 0:
        return max(0, v - amount)
    else:
        return min(0, v + amount)


PLAYER_ANIM_PERIOD = 0.25 * FPS


class Player:
    def __init__(self, x, y):
        self.w = 8
        self.h = 8
        self.x = x# + (8-self.w)//2
        self.y = y
        self.vy = 0
        self.vx = 0
        self.collide_door = False
        self.collide_key = False

        self.direction = 'r'
        self.anim_state = 0
        self.anim_timer = 0

    def update(self):
        # Physics
        self.y += self.vy

        if features['friction']:
            self.vy = apply_friction(self.vy, FRICTION_AIR)

        # Collisions
        top = self.col_top()
        if top != False:
            self.vy = max(0, self.vy)
            self.y = top
            if not features['gravity'] and pyxel.btnp(pyxel.KEY_DOWN):
                self.vy = PLAYER_SPEED

        bottom = self.col_bottom()
        if bottom == False:
            # Gravity
            if features['gravity']:
                self.vy += GRAVITY
        else:
            self.vy = min(0, self.vy)
            self.y = bottom - self.h

            if features['gravity']:
                if features['jump'] and pyxel.btnp(pyxel.KEY_UP):
                    self.vy = -PLAYER_JUMP
            else:
                if pyxel.btnp(pyxel.KEY_UP):
                    self.vy = -PLAYER_SPEED

        self.x += self.vx

        if features['friction']:
            self.vx = apply_friction(
                self.vx,
                FRICTION_GROUND if (bottom and features['gravity']) else FRICTION_AIR)

        left = self.col_left()
        if left != False:
            self.x = left
            self.vx = max(0, self.vx)
            if not features['gravity'] and features['right'] and pyxel.btnp(pyxel.KEY_RIGHT):
                self.vx = PLAYER_SPEED
        else:
            if features['gravity'] and features['left'] and pyxel.btn(pyxel.KEY_LEFT):
                self.vx = -PLAYER_SPEED

        right = self.col_right()
        if right != False:
            self.x = right - self.w
            self.vx = min(0, self.vx)
            if not features['gravity'] and features['left'] and pyxel.btnp(pyxel.KEY_LEFT):
                self.vx = -PLAYER_SPEED
        else:
            if features['gravity'] and features['right'] and pyxel.btn(pyxel.KEY_RIGHT):
                self.vx = PLAYER_SPEED

        #self.cols = [
        #    pyxel.tilemap(0).get(tx, ty)
        #    for tx in range(int((self.x-1)//8), int((self.x+self.w)//8)+1)
        #    for ty in range(int((self.y-1)//8), int((self.y+self.h)//8)+1)
        #]

        tile = pyxel.tilemap(0).get(int(self.x+self.w/2)//8, int(self.y+self.h/2)//8)
        self.collide_door = tile == TILE_DOOR
        self.collide_key = tile == TILE_KEY

        # Animation
        self.anim_timer += 1
        if self.anim_timer >= PLAYER_ANIM_PERIOD:
            self.anim_timer = 0
            self.anim_state = (self.anim_state + 1) % 2

        if self.vx < 0:
            self.direction = 'l'
        elif self.vx > 0:
            self.direction = 'r'

        # Suppress animations if not moving
        if self.vx == 0 or not features['animations']:
            self.anim_state = 0

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
        if self.direction == 'r':
            frame = 1 + self.anim_state
        else:
            frame = 3 + self.anim_state
        img = 0 if features['sprites'] else 1
        pyxel.blt(self.x, self.y, img, frame*8+4-self.w//2, 0, self.w, self.h, 0)


class GuiMenu:
    def __init__(self, title, item_names, items, selected=0):
        self.title = title
        self.item_names = item_names
        self.items = items
        self.selected = selected

    def update(self):
        if pyxel.btnp(pyxel.KEY_UP, 0.5 * FPS, 0.1 * FPS):
            self.selected = max(self.selected - 1, 0)

        if pyxel.btnp(pyxel.KEY_DOWN, 0.5 * FPS, 0.1 * FPS):
            self.selected = min(self.selected + 1, len(self.items)-1)

        if pyxel.btnr(pyxel.KEY_ENTER):
            return True

        return False

    def draw(self):
        text = self.title + '\n\n'

        for i, item in enumerate(self.items):
            if i == self.selected:
                text += ' [X] ' + self.item_names[item] + '\n'
            else:
                text += ' [ ] ' + self.item_names[item] + '\n'

        draw_textbox(text[:-1])

    def selected_item(self):
        return self.items[self.selected]


class SceneStack:
    def __init__(self):
        self.scenes = []
        self.menus = []

    def push_scene(self, scene):
        scene.scene_stack = self
        scene.load()
        self.scenes.append(scene)

    def pop_scene(self):
        return self.scenes.pop()

    def clear_scenes(self):
        while len(self.scenes) > 0:
            self.pop_scene()

    def push_menu(self, menu):
        menu.scene_stack = self
        menu.load()
        self.menus.append(menu)

    def pop_menu(self):
        return self.menus.pop()

    def clear_menus(self):
        while len(self.menus) > 0:
            self.pop_menu()

    def top_scene(self):
        if len(self.scenes) > 0:
            return self.scenes[-1]
        else:
            return None

    def top_menu(self):
        if len(self.menus) > 0:
            return self.menus[-1]
        else:
            return None


class Scene:
    def load(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class Menu:
    def load(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


def find_in_level(tile):
    level_map = pyxel.tilemap(0).data[:GAME_TILES_W,:GAME_TILES_H]
    y, x = np.where(level_map == tile)
    return x[0], y[0]


def erase_tile(x, y, erase_with=0):
    pyxel.tilemap(0).set(x, y, erase_with)


def erase_all_tiles_like(tile, erase_with=0):
    level_map = pyxel.tilemap(0).data[:GAME_TILES_W,:GAME_TILES_H]
    ys, xs = np.where(level_map == tile)
    for (x, y) in zip(xs, ys):
        erase_tile(x, y, erase_with)


class LevelScene(Scene):
    def __init__(self, level):
        self.level = level
        self.dialog = None

    def load(self):
        pyxel.tilemap(0).copy(
                0, 0, 1,
                self.level * GAME_TILES_W, 0,
                GAME_TILES_W, GAME_TILES_H)

        # Player location
        try:
            px, py = find_in_level(TILE_PLAYER)
            erase_tile(px, py)
        except IndexError:
            raise GameError("No player on level {}".format(self.level))

        # Door location
        try:
            dx, dy = find_in_level(TILE_DOOR)
        except IndexError:
            raise GameError("No door on level {}".format(self.level))

        self.player = Player(px * 8, py * 8)

        if not features['keys']:
            erase_all_tiles_like(TILE_KEY)
        if not features['locks']:
            erase_all_tiles_like(TILE_LOCK)

        if self.level > FIRST_LEVEL:
            self.scene_stack.push_menu(SacrificeMenu())

        if features['tutorial']:
            if self.level - FIRST_LEVEL < len(TUTORIAL_TEXTS):
                self.scene_stack.push_menu(TutorialMenu(TUTORIAL_TEXTS[self.level - FIRST_LEVEL]))

    def update(self):
        if pyxel.btn(pyxel.KEY_TAB):
            self.scene_stack.push_menu(PauseMenu())

        if features['player']:
            self.player.update()

        if self.player.collide_door:
            # Next level transition
            self.scene_stack.pop_scene()
            if self.level < LAST_LEVEL:
                self.scene_stack.push_scene(LevelScene(self.level + 1))
            else:
                if features['tutorial']:
                    self.scene_stack.push_menu(GoodEndgameMenu())
                else:
                    self.scene_stack.push_menu(BadEndgameMenu())

        if self.player.collide_key:
            erase_all_tiles_like(TILE_KEY)
            erase_all_tiles_like(TILE_LOCK, erase_with=TILE_UNLOCKED)

        x, y = int(self.player.x//8), int(self.player.y//8)
        if x < -2 or x > GAME_TILES_W+1 or y < -2 or y > GAME_TILES_H+1:
            # Restart level if we leave the boundaries
            if self.scene_stack.top_scene().level > FIRST_LEVEL:
                features[sacrifices.pop()] = True
            self.load()

    def draw(self):
        if features['sprites']:
            pyxel.tilemap(0).refimg = 0
        else:
            pyxel.tilemap(0).refimg = 1
        pyxel.bltm(0, 0, 0, 0, 0, 16, 16)

        if features['player']:
            self.player.draw()

        if self.dialog is not None:
            draw_textbox(self.dialog, y='bottom')


class SacrificeMenu(Menu):
    def load(self):
        print(last_sacrifice)
        active_features = [name for name, state in features.items() if state]
        items = ['animations', 'sprites', 'windows', 'rendering', 'tutorial', 'keys', 'locks', 'friction', 'gravity', 'collisions', 'left', 'right', 'jump', 'player', 'game']
        items = [item for item in items if item in active_features]
        print(items)

        selected = np.where(last_sacrifice == np.array(items))[0]
        selected = selected[0] if len(selected) > 0 else 0
        self.menu = GuiMenu("Choose a sacrifice:", features_name, items, selected)

    def update(self):
        if self.menu.update():
            self.scene_stack.pop_menu()

            feature = self.menu.selected_item()
            print("Sacrificed", features_name[feature])
            features[feature] = False
            sacrifices.append(feature)
            last_sacrifice = feature

            if not features['keys']:
                erase_all_tiles_like(TILE_KEY)
            if not features['locks']:
                erase_all_tiles_like(TILE_LOCK)

    def draw(self):
        self.menu.draw()


class TextSequence:
    def __init__(self, texts, color=TEXT_COL, init_delay=0, delay=FPS):
        self.texts = texts
        self.iter = 0
        self.color = color
        self.delay = delay
        self.timer = -init_delay

    def update(self):
        self.timer += 1
        if self.timer > self.delay:
            if pyxel.btn(pyxel.KEY_ENTER):
                self.iter += 1
                self.timer = 0
                if self.iter >= len(self.texts):
                    return True
        return False

    def get_current_text(self):
        return self.texts[self.iter]

    def draw(self):
        if self.timer > self.delay:
            draw_textbox(self.get_current_text(), color=self.color)


class BadEndgameMenu(Menu):
    def load(self):
        self.scene_stack.push_scene(BadEndgameScene())
        self.text_sequence = TextSequence([
"""This was the last
puzzle, I think.""",

"""What am I left with?""",

"""I can only see and
think, but there is
no-one to share my
thoughts with.""",

"""I guess, I won?""",
        ], color=3, init_delay=2*FPS, delay=3*FPS)

    def update(self):
        if self.text_sequence.update():
            pyxel.quit()

    def draw(self):
        self.text_sequence.draw()


class BadEndgameScene(Scene):
    def load(self):
        pyxel.tilemap(0).copy(
                0, 0, 0,
                15 * GAME_TILES_W, 0,
                GAME_TILES_W, GAME_TILES_H)

    def update(self):
        pass

    def draw(self):
        if features['sprites']:
            pyxel.tilemap(0).refimg = 0
        else:
            pyxel.tilemap(0).refimg = 1
        pyxel.bltm(0, 0, 0, 0, 0, 16, 16)


class GoodEndgameMenu(Menu):
    def load(self):
        features['rendering'] = True
        self.text_sequence = TextSequence([
"""You won!...""",

"""But at what cost?""",

"""You abandoned the
beauty of this
world...""",

"""You took the harder
path...""",

"""And ultimately, you
surrendered to
darkness...""",

"""...All that, for me?""",

"""...""",

"""I don't know what
to say.""",

"""...""",

"""Thank you."""
        ], init_delay=3*FPS, delay=2*FPS)

    def update(self):
        if self.text_sequence.update():
            self.scene_stack.push_menu(CreditMenu(12))

    def draw(self):
        self.text_sequence.draw()


class CreditMenu(Menu):
    def __init__(self, background):
        self.background = background

    def load(self):
        self.text_sequence = TextSequence([
"""A game by

Xavier Lambein

@xlambein
lambein.xyz""",

"""Made in 48 hours
during the game jam
Ludum Dare 43.""",

"""Thank you so much
for playing!""",
        ], 2)

    def update(self):
        if self.text_sequence.update():
            pyxel.quit()

    def draw(self):
        pyxel.cls(self.background)
        self.text_sequence.draw()


class PauseMenu(Menu):
    def load(self):
        if self.scene_stack.top_scene().level > FIRST_LEVEL:
            items = ['resume', 'restart', 'previous', 'quit']
        else:
            items = ['resume', 'restart', 'quit']
        item_names = {
            'resume': "Resume",
            'restart': "Restart level",
            'previous': "Previous level",
            'quit': "Quit",
        }
        self.menu = GuiMenu("Game paused", item_names, items)

    def update(self):
        if self.menu.update():
            self.scene_stack.pop_menu()

            selected = self.menu.selected_item()

            # Restart level
            if selected == 'restart':
                if self.scene_stack.top_scene().level > FIRST_LEVEL:
                    features[sacrifices.pop()] = True
                self.scene_stack.top_scene().load()

            # Previous level
            elif selected == 'previous':
                features[sacrifices.pop()] = True
                level = self.scene_stack.pop_scene().level
                if level-1 > FIRST_LEVEL:
                    features[sacrifices.pop()] = True
                self.scene_stack.push_scene(LevelScene(level - 1))

            # Quit
            elif selected == 'quit':
                pyxel.quit()

    def draw(self):
        self.menu.draw()


class TutorialMenu(Menu):
    def __init__(self, text):
        self.dialog = text

    def update(self):
        if pyxel.btnr(pyxel.KEY_ENTER):
            self.scene_stack.pop_menu()

    def draw(self):
        draw_textbox(self.dialog, w=12)


TUTORIAL_TEXTS = [

"""Welcome to this game!

Reach any door to finish
a level.
Use the arrow keys to
move and jump.

Press Tab in-game to
show the menu.  You can
restart from there if
you're stuck.

Press Enter to continue.""",

"""Before entering a level,
you must sacrifice one
feature of this game.

Select a sacrifice with
the arrows keys and
submit with Enter.

From the menu, you can
go back to the previous
level to change a
sacrifice.""",

"""To get past these
blocks you're gonna
need to get a hold of
this key.

You're doing great, so
it should be easy for
you!  Good luck!""",

"""Here's my final piece
of information for you;
when gravity is gone,
the only way to move is
to push against a
surface.

I think it's only
useful for the endgame,
though, but I'm not
sure.  I haven't been
there.  I wish I
could...

Okay, well.  I guess
that's all!  Good luck
and farewell!""",

"""Oh, I'm still here?

You should sacrifice me.
There are more important
features in this game
than me.

I'm "Help text" in the
list.

Really, it'll be much
easier for you that way.""",

"""I haven't seen this
level in ages!

Wait--

Why are you doing this?
Why am I still with
you?""",

"""You are making your
life so much harder,
you know that?

Maybe you just don't
realize it yet.""",

"""See?  That's what I
meant.

This puzzle would've
been so much easier
with a jump.""",

"""You know, I don't
remember ever existing
that long.

Like--  I have never
seen this level.  This
is exciting.""",

"""...Hey, you're still
here?

Listen, I'm sorry I was
rude earlier.

It's just.  I don't
understand why you'd
do this for me?

But... I am grateful.
I've always wanted to
go that far in the
game."""

]


def draw_textbox(text, x=None, y=None, w=None, h=None, color=TEXT_COL):
    lines = text.split('\n')
    lens = map(len, lines)

    cols = reduce(max, lens)
    rows = len(lines)

    if w is None:
        w = int(np.ceil(cols * TEXT_WIDTH / 8))
    if h is None:
        h = int(np.ceil(rows * TEXT_HEIGHT / 8))

    if features['sprites']:
        TSX, TSY = 1, 1
    else:
        TSX, TSY = 4, 1

    if x is None:
        x = (GAME_TILES_W - w) // 2
    if y is None:
        y = (GAME_TILES_H - h) // 2
    elif y == 'bottom':
        y = (GAME_TILES_H - h) - 1

    if features['windows']:
        pyxel.blt((x-1)*8, (y-1)*8, 2, (TSX-1)*8, (TSY-1)*8, 8, 8, colkey=0)
        pyxel.blt((x+w)*8, (y-1)*8, 2, (TSX+1)*8, (TSY-1)*8, 8, 8, colkey=0)
        pyxel.blt((x-1)*8, (y+h)*8, 2, (TSX-1)*8, (TSY+1)*8, 8, 8, colkey=0)
        pyxel.blt((x+w)*8, (y+h)*8, 2, (TSX+1)*8, (TSY+1)*8, 8, 8, colkey=0)

        for i in range(w):
            pyxel.blt((x+i)*8, (y-1)*8, 2, TSX*8, (TSY-1)*8, 8, 8, colkey=0)
            pyxel.blt((x+i)*8, (y+h)*8, 2, TSX*8, (TSY+1)*8, 8, 8, colkey=0)

        for j in range(h):
            pyxel.blt((x-1)*8, (y+j)*8, 2, (TSX-1)*8, TSY*8, 8, 8, colkey=0)
            pyxel.blt((x+w)*8, (y+j)*8, 2, (TSX+1)*8, TSY*8, 8, 8, colkey=0)

        for i in range(w):
            for j in range(h):
                pyxel.blt((x+i)*8, (y+j)*8, 2, TSX*8, TSY*8, 8, 8)

        pyxel.text(x*8, y*8, text, color)

    else:
        pyxel.text(x*8+1, y*8, text, color)
        pyxel.text(x*8, y*8, text, 7)


class App:
    def __init__(self):
        pyxel.init(GAME_TILES_W*8, GAME_TILES_H*8,
            caption="Sacrifice This Game",
            fps=FPS,
            scale=8)

        pyxel.load("resource.pyxel")

        self.scene_stack = SceneStack()
        self.scene_stack.push_scene(LevelScene(10))

        pyxel.run(self.update, self.draw)

    def update(self):
        if not features['game']:
            pyxel.quit()

        menu = self.scene_stack.top_menu()
        if menu is not None:
            menu.update()
        else:
            scene = self.scene_stack.top_scene()
            if scene is not None:
                scene.update()
            else:
                pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        
        if features['rendering']:
            scene = self.scene_stack.top_scene()
            if scene is not None:
                scene.draw()

            menu = self.scene_stack.top_menu()
            if menu is not None:
                menu.draw()


App()

