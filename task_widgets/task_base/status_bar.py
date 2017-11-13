# -*- coding: utf-8 -*-
from kivy.animation import Animation
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex

from settings import FILL_COLOR, FILL_COLOR_SEMITRANSPARENT
from utils import _, import_kv
from library_widgets import AnimationMixin

import_kv(__file__)


class TaskStatusBarCorrectness(Label, AnimationMixin):
    mistakes_count = NumericProperty()
    correct_count = NumericProperty()
    CORRECT_COLOR = FILL_COLOR
    INCORRECT_COLOR = (1, 1, 1, 1)
    INCOMPLETE_COLOR = FILL_COLOR_SEMITRANSPARENT
    CLIP_ANGLE = -3
    PATTERN = u"[color=#408742ff][font=glyphicons]\uE013[/font]%s[/color]  " \
              u"[color=#eb542cff][font=glyphicons]\uE014[/font]%s[/color]"

    def show(self, *args):
        self.animation.start(self)

    def update_text(self, *_):
        self.text = self.PATTERN % (self.correct_count, self.mistakes_count)

    def __init__(self, **kwargs):
        super(TaskStatusBarCorrectness, self).__init__(**kwargs)
        self.bind(mistakes_count=self.update_text,
                  correct_count=self.update_text)
        self.update_text()


class TaskStatusBarTime(FloatLayout, AnimationMixin):
    PATTERN = "[b]%.1f[/b] [size=16]sec[/size]"
    seconds = NumericProperty(0)
    label = ObjectProperty()

    def update_seconds(self, instance, value):
        instance.label.text = self.PATTERN % value

    def show(self, *args):
        self.animation.start(self)

    def on_label(self, instance, value):
        value.text = self.PATTERN % self.seconds

    def __init__(self, **kwargs):
        super(TaskStatusBarTime, self).__init__(**kwargs)
        self.bind(seconds=self.update_seconds)


class TaskStatusBarPoints(Label):
    points = NumericProperty()
    label_size = NumericProperty()

    def on_points(self, instance, value):
        if self.points:
            self.text = _("%s\n[size=%s]POINTS[/font]") % (self.points,
                                                           int(self.label_size))
        else:
            self.text = ""

    on_label_size = on_points


class TaskStatusBar(BoxLayout):
    time_widget = ObjectProperty()
    correctness_widget = ObjectProperty()
    points_widget = ObjectProperty()
    time = NumericProperty()
    mistakes_count = NumericProperty()
    correct_count = NumericProperty()
    points = NumericProperty()

    def on_points(self, status, value):
        self.points_widget.points = value

    def on_correct_count(self, status, value):
        self.correctness_widget.correct_count = value

    def on_mistakes_count(self, status, value):
        self.correctness_widget.mistakes_count = value
        original_color = tuple(self.time_widget.label.color)
        time_label_animation = Animation(color=get_color_from_hex("eb542cff"), d=1) + Animation(color=original_color,
                                                                                                d=1)
        time_label_animation.start(self.time_widget.label)
        time_label_animation.start(self.points_widget)

    def on_time(self, status, value):
        self.time_widget.seconds = value

    def show(self):
        self.time_widget.show()
        self.correctness_widget.show()
