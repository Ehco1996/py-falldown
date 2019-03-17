import random
import pyxel

WIDTH = 80
HEIGHT = 140
FPS = 100

COL_DEATH = 6
COL_WIN = 10

PLAY_MIN_Y = 20
PLAY_MAX_Y = HEIGHT


class Ball:

    RADIUS = 3
    MOVE_SPEED = 0.9
    FALL_SPEED = 0.5

    DEFAULT_X = 5
    DEFAULT_Y = 5

    def __init__(self, x, y, r, col):
        self.x = x
        self.y = x
        self.r = r
        self.col = col

        self.__max_x__ = WIDTH - r - 1
        self.__min_x__ = r

        self.__max_y__ = HEIGHT - r - 1
        self.__min_y__ = r

    @property
    def edge_down(self):
        return round(self.y + self.r, 2)

    @property
    def edge_left(self):
        return round(self.x - self.r, 2)

    @property
    def edge_right(self):
        return round(self.x + self.r, 2)

    def __move__(self, x=None, y=None):

        if x:
            if x <= self.__min_x__:
                x = self.__min_x__
            if x >= self.__max_x__:
                x = self.__max_x__
            self.x = x

        if y:
            if y <= self.__min_y__:
                y = self.__min_y__
            if y >= self.__max_y__:
                y = self.__max_y__
            self.y = y

    def move_x_by_speed(self, speed):
        self.__move__(x=self.x + speed)

    def move_y_by_speed(self, speed):
        self.__move__(y=self.y + speed)

    def sync_with_line(self, line):
        self.y = line.y - self.r

    @classmethod
    def gen_ball(cls):
        return cls(x=cls.DEFAULT_X, y=cls.DEFAULT_Y, r=Ball.RADIUS, col=8)


class GapLine:
    """
    Line like this：  ————    ———
                      x1     x2   x3   x4
    """

    GAP_WIDTH = Ball.RADIUS * 4
    GROUND_WIDTH = WIDTH
    UP_SPEED = 0.1

    def __init__(self, x1, x2, x3, x4, y):
        self.x1 = x1
        self.x2 = x2
        self.x3 = x3
        self.x4 = x4
        self.y = y

    def __repr__(self):
        return f"gap:[{self.x2},{self.x3}],y:{self.y}"

    def move_y_by_speed(self, speed):
        self.y += speed

    @classmethod
    def gen_by_gap_width(cls, y, width=GAP_WIDTH):
        gap_start = random.randint(0 + width, cls.GROUND_WIDTH - width)
        return cls(x1=0, x2=gap_start, x3=gap_start + width, x4=cls.GROUND_WIDTH, y=y)

    def check_touch(self, ball: Ball):
        check_x = self.x2 > ball.edge_left or self.x3 < ball.edge_right
        check_y = abs(round(ball.edge_down - self.y, 2)) < ball.r
        return check_x and check_y


class FallDown:

    LINE_GAP = Ball.RADIUS * 4

    def __init__(self):
        self.ball = Ball.gen_ball()
        self.gap_lines = []

        self.win = False

        pyxel.init(width=WIDTH, height=HEIGHT, caption="Fall Down", scale=5, fps=FPS)

    def update(self):
        x_speed = 0

        if pyxel.btn(pyxel.KEY_LEFT):
            x_speed = -Ball.MOVE_SPEED
        elif pyxel.btn(pyxel.KEY_RIGHT):
            x_speed = Ball.MOVE_SPEED

        self.update_gap_lines()
        self.update_ball(x_speed, Ball.FALL_SPEED)

        self.check_win()

    def update_gap_lines(self):
        if not self.gap_lines:
            for y in range(PLAY_MIN_Y, PLAY_MAX_Y + self.LINE_GAP, self.LINE_GAP):
                self.gap_lines.append(GapLine.gen_by_gap_width(y))

        need_pop = -1
        for gap in self.gap_lines:
            if gap.y < PLAY_MIN_Y - self.LINE_GAP:
                need_pop += 1
            gap.move_y_by_speed(-GapLine.UP_SPEED)

        for index in range(0, need_pop):
            self.gap_lines.pop(index)
            last_line = self.gap_lines[-1]
            self.gap_lines.append(
                GapLine.gen_by_gap_width(y=last_line.y + self.LINE_GAP)
            )

    def update_ball(self, x_speed, y_speed):
        def auto_fall_down():
            ball = self.ball
            for line in self.gap_lines:
                if line.check_touch(ball):
                    ball.sync_with_line(line)
            ball.move_y_by_speed(y_speed)

        auto_fall_down()
        self.ball.move_x_by_speed(x_speed)

    def check_win(self):
        if self.ball.y >= HEIGHT - self.ball.r * 2:
            self.win = True

    def draw(self):
        pyxel.cls(0)
        self.draw_gap_lines()
        self.draw_ball()

        if self.win:
            self.draw_text("YOU WIN !")

    def draw_ball(self):
        ball = self.ball
        pyxel.circ(x=ball.x, y=ball.y, r=ball.r, col=ball.col)
        pyxel.circb(x=ball.x, y=ball.y, r=ball.r, col=ball.col)

    def draw_gap_lines(self):
        def draw_line_by_gap(gap):
            pyxel.line(x1=gap.x1, y1=gap.y, x2=gap.x2, y2=gap.y, col=9)
            pyxel.line(x1=gap.x3, y1=gap.y, x2=gap.x4, y2=gap.y, col=9)

        for gap in self.gap_lines:
            draw_line_by_gap(gap)

    def draw_text(self, display_text):
        pyxel.cls(0)
        text_width = len(display_text) * pyxel.constants.FONT_WIDTH
        text_x = (WIDTH - text_width) / 2
        text_y = HEIGHT / 2
        pyxel.text(text_x, text_y, display_text, COL_WIN)

    def run(self):
        pyxel.run(self.update, self.draw)


FallDown().run()
