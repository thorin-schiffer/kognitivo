# -*- coding: utf-8 -*-
from datetime import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from random import uniform

from kivy.properties import NumericProperty, ObjectProperty
from task_base.intro_hint import IntroHint
from task_widgets.task_base.mixins import StartImmediatelyMixin

from answer_widgets import AnswerButton, BaseAnswerWidget
from library_widgets import OnPressAnimationMixin, ColorSquare
from task_widgets.task_base.base import BaseTask
from utils import import_kv

import_kv(__file__)


class WhiteSquare(ColorSquare, AnswerButton, OnPressAnimationMixin):
    task_size = NumericProperty()

    def __init__(self, **kwargs):
        super(WhiteSquare, self).__init__(**kwargs)
        self.is_shown = False
        self.pressed = False
        self.bind(on_press=self.do_on_press)

    def place_randomly(self):
        self.pos_hint = {
            "center_x": uniform(self.size_hint[0] / 2, 1 - self.size_hint[0] / 2),
            "center_y": uniform(self.size_hint[1] / 2, 1 - self.size_hint[1] / 2),
        }

    def on_is_shown(self, instance, value):
        if value:
            self.show()
        else:
            self.hide()

    def do_on_press(self, _):
        self.pressed = True

    def hide(self, *_):
        self.opacity = 0
        self.is_shown = False
        self.pressed = False

    def show(self):
        self.opacity = 1
        self.is_shown = True
        self.pressed = False


class WhiteSquaresDescriptionWidget(Label):
    pass


class WhiteSquaresAnswerWidget(RelativeLayout, BaseAnswerWidget):
    square = ObjectProperty()

    def get_values_widgets(self, *args, **kwargs):
        return {True: [self.square]}


class IntroHintWhiteSquares(IntroHint):
    pass


class WhiteSquares(BaseTask, StartImmediatelyMixin):
    TASK_KEY = "white_squares"
    SIZE = 8
    START_DURATION = 1.
    DURATION_REDUCTION_STEP = 0.99
    MAX_DURATION = 15
    REPEATS_MIN_DELAY = 0.1
    REPEATS_MAX_DELAY = 1.
    MISTAKE_FINE = 0
    INTRO_HINT_CLASS = IntroHintWhiteSquares
    DESCRIPTION_WIDGET_CLASS = WhiteSquaresDescriptionWidget
    ANSWER_WIDGET_CLASS = WhiteSquaresAnswerWidget

    def on_mistakes_count(self, *args, **kwargs):
        pass

    def __init__(self, **kwargs):
        self.square = None
        self.current_duration = self.START_DURATION
        self.current_point_square = None
        self.repeats = 0
        self._start_button_time = None
        self.mistakes_count = 0
        self.start_time = None
        super(WhiteSquares, self).__init__(**kwargs)
        self.correct_answer = True

    def on_correct_answer(self, button):
        App.get_running_app().sounds['success'].play()
        self.num_succeed += 1
        self.seconds_to_success += (datetime.now() - self._start_button_time).total_seconds()
        self.current_duration *= self.DURATION_REDUCTION_STEP

    def on_incorrect_answer(self, button):
        App.get_running_app().sounds['fail'].play()
        from managers.vibration import vibration_manager
        vibration_manager.vibrate(100)

        self.mistakes_count += 1
        self.seconds_to_success += self.current_duration

    def _check_answer(self, button):
        if button.is_shown:
            self.on_correct_answer(button)
        else:
            self.on_incorrect_answer(button)

        self._calculate_seconds_to_success()

        if self.repeats >= self.SIZE:
            self.finish()

    def unbind_buttons(self):
        self.square.unbind(on_press=self._check_answer)

    def _calculate_seconds_to_success(self, *_):
        pass

    def hide_square(self, _=None):
        if not self.square.pressed:
            self.on_incorrect_answer(self.square)
            if self.repeats >= self.SIZE:
                self.finish()

        self._calculate_seconds_to_success()

        self.square.hide()

        if self.repeats < self.SIZE:
            timeout = uniform(self.REPEATS_MIN_DELAY,
                              self.REPEATS_MAX_DELAY)
            Clock.schedule_once(self.show_square, timeout)

    def show_square(self, _=None):
        self.square.place_randomly()
        self.square.show()

        self._start_button_time = datetime.now()
        self.repeats += 1
        Clock.schedule_once(self.hide_square, timeout=self.current_duration)

    def finish(self, update_status=True):
        Clock.unschedule(self.show_square)
        Clock.unschedule(self.hide_square)
        self.unbind_buttons()
        super(WhiteSquares, self).finish(update_status)

    def get_answer_widget(self):
        container = super(WhiteSquares, self).get_answer_widget()

        self.square = WhiteSquare(on_press=self._check_answer)
        container.square = self.square
        container.add_widget(self.square)
        return container

    def on_intro_hint_hide(self, *args, **kwargs):

        timeout = uniform(self.REPEATS_MIN_DELAY,
                          self.REPEATS_MAX_DELAY)

        Clock.schedule_once(self.show_square, timeout=timeout)
