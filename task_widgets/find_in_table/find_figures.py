# -*- coding: utf-8 -*-
import random
from kivy.app import App
from kivy.core.image import Image

from kivy.properties import StringProperty, ObjectProperty

from answer_widgets import DisappearOnCorrectAnswerButton
from task_widgets.task_base.intro_hint import IntroHint
from utils import _, import_kv
from .find_in_table import FindInTable, FindInTableDescriptionWidget, FindInTableAnswerWidget

import_kv(__file__)


class IntroHintFindFigures(IntroHint):
    pass


class FindFiguresDescriptionWidget(FindInTableDescriptionWidget):
    pass


class FindFiguresAnswerButton(DisappearOnCorrectAnswerButton):
    NOT_CHECKED_COLOR = (1, 1, 1, 1)
    icon_src = StringProperty()
    icon = ObjectProperty()

    def on_icon_src(self, instance, value):
        self.icon = Image(value)


class FindFiguresAnswerWidget(FindInTableAnswerWidget):
    BUTTON_WIDGET_CLASS = FindFiguresAnswerButton

    def add_variants(self, variants, callback, text_modifier=unicode, right_figures=None):
        count = 0
        for figure_name, figure_icon in variants:
            value = right_figures[figure_name] == figure_icon
            if value:
                count += 1
            button = self.BUTTON_WIDGET_CLASS(text=figure_name,
                                              value=value,
                                              on_press=callback,
                                              icon_src=figure_icon)
            self.buttons.append(button)
            self.add_widget(button)
        return count


class FindFigures(FindInTable):
    SIZE = 3
    TASK_KEY = "find_figures"
    INTRO_HINT_CLASS = IntroHintFindFigures
    DESCRIPTION_WIDGET_CLASS = FindFiguresDescriptionWidget
    ANSWER_WIDGET_CLASS = FindFiguresAnswerWidget
    EFFICIENCY_TO_POINTS = 20000

    def __init__(self, **kwargs):
        super(FindFigures, self).__init__(**kwargs)
        self.point_count = None
        self.FIGURES = {
            _("TRIANGLE"): "atlas://data/atlas/tasks/triangle",
            _("SQUARE"): "atlas://data/atlas/tasks/square",
            _("STAR"): "atlas://data/atlas/tasks/star",
            _("PENTAGON"): "atlas://data/atlas/tasks/pentagon",
            _("CIRCLE"): "atlas://data/atlas/tasks/circle",
            _("DIAMOND"): "atlas://data/atlas/tasks/diamond",
        }

    def generate_alphabet(self):

        figures = list(self.FIGURES.items())
        random.shuffle(figures)
        alphabet = figures[:self.SIZE]

        for i in xrange((self.SIZE - 1) * self.SIZE):
            name = random.choice(self.FIGURES.keys())
            incorrect_figures = [value for value in self.FIGURES.values() if value != self.FIGURES[name]]
            alphabet.append(
                (name, random.choice(incorrect_figures))
            )
        return alphabet

    def get_description_widget(self, **kwargs):
        self.correct_answer = True
        widget = super(FindInTable, self).get_description_widget(**kwargs)
        return widget

    def get_answer_widget(self):

        values = self.generate_alphabet()
        random.shuffle(values)
        widget = super(FindInTable, self).get_answer_widget(rows=self.SIZE, cols=self.SIZE)
        self.point_count = widget.add_variants(values, self._check_answer, right_figures=self.FIGURES)
        return widget

    def on_correct_answer(self, button):
        App.get_running_app().sounds['success'].play()
        button.mark_correct()
        button.unbind(on_press=self._check_answer)
        self.num_succeed += 1

        if self.num_succeed >= self.point_count:
            self.finish()
