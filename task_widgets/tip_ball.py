import random
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout

from kivy.properties import NumericProperty, ObjectProperty, ListProperty, BooleanProperty
from task_base.intro_hint import IntroHint
from task_widgets.task_base.mixins import StartImmediatelyMixin

from answer_widgets import ButtonsAnswerWidget, AnswerButton
from settings import FILL_COLOR_SEMITRANSPARENT, FILL_COLOR_QUASITRANSPARENT
from task_widgets.task_base.base import BaseTask
from utils import import_kv

import_kv(__file__)


class Ball(AnswerButton):
    radius = NumericProperty(.2)
    time = NumericProperty(1.)
    RADIUS_STEP = .9
    TIME_STEP = .8
    color = ListProperty(FILL_COLOR_SEMITRANSPARENT)
    move_animation = ObjectProperty()
    to_animate = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(Ball, self).__init__(**kwargs)
        self.value = True

    def on_press(self, *args, **kwargs):
        if not self.to_animate:
            self.radius = 0
            return
        Animation(radius=self.radius * self.RADIUS_STEP, t=self.transition, d=.25).start(self)
        self.time *= self.TIME_STEP
        mark_animation = Animation(color=FILL_COLOR_QUASITRANSPARENT,
                                   duration=.25,
                                   t='out_expo') + Animation(color=self.color,
                                                             duration=.25,
                                                             t='in_out_cubic')
        mark_animation.start(self)
        self.move_random()

    def move_random(self, *args, **kwargs):
        if self.move_animation is not None:
            self.move_animation.cancel(self)

        if not self.to_animate:
            self.radius = 0
            return
        x = random.uniform(self.radius, 1 - self.radius)
        y = random.uniform(self.radius, 1 - self.radius)

        self.move_animation = Animation(pos_hint={"center_x": x,
                                                  "center_y": y}, duration=self.time, t='in_out_cubic')
        self.move_animation.bind(on_complete=self.move_random)
        self.move_animation.start(self)


class TipBallIntroHint(IntroHint):
    pass


class PlayArea(FloatLayout, ButtonsAnswerWidget):
    BUTTON_WIDGET_CLASS = Ball
    ball = ObjectProperty()


class TipBall(BaseTask, StartImmediatelyMixin):
    SIZE = 10
    TASK_KEY = "tip_ball"
    MAX_DURATION = 10
    INTRO_HINT_CLASS = TipBallIntroHint
    ANSWER_WIDGET_CLASS = PlayArea

    def __init__(self, **kwargs):
        super(TipBall, self).__init__(**kwargs)
        self.correct_answer = True

    def add_main_widgets(self):
        self.main_area.add_widget(self.get_answer_widget())
        ball = Ball(on_press=self._check_answer)
        self.answer_widget.ball = ball
        self.answer_widget.buttons.append(ball)
        self.answer_widget.add_widget(ball)
        self.answer_widget.ball.move_random()

    def _check_answer(self, widget=None):
        if not self.successful:
            self.num_succeed += 1

            if self.num_succeed >= self.SIZE:
                self.finish()

    def finish(self, update_status=True):
        super(TipBall, self).finish(update_status)
        self.answer_widget.ball.to_animate = False
