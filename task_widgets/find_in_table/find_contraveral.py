# -*- coding: utf-8 -*-
import random
from kivy.app import App

from answer_widgets import DisappearOnCorrectAnswerButton
from task_widgets.task_base.intro_hint import IntroHint
from utils import _, import_kv
from .find_in_table import FindInTable, FindInTableDescriptionWidget, FindInTableAnswerWidget

import_kv(__file__)


class IntroHintFindContraversal(IntroHint):
    pass


class FindContraversalDescriptionWidget(FindInTableDescriptionWidget):
    pass


class FindContraversalAnswerButton(DisappearOnCorrectAnswerButton):
    NOT_CHECKED_COLOR = (1, 1, 1, 1)


class FindContraversalAnswerWidget(FindInTableAnswerWidget):
    BUTTON_WIDGET_CLASS = FindContraversalAnswerButton
    TEXT_PATTERN = "[color=%s]%s[/color]"

    def add_variants(self, variants, callback, text_modifier=unicode, right_colors=None):
        count = 0
        for color_name, color_hex in variants:
            value = right_colors[color_name] == color_hex
            if value:
                count += 1
            button = self.BUTTON_WIDGET_CLASS(text=self.TEXT_PATTERN % (color_hex, color_name),
                                              value=value,
                                              on_press=callback)
            self.buttons.append(button)
            self.add_widget(button)
        return count


class FindContraversal(FindInTable):
    SIZE = 3
    TASK_KEY = "find_contraversal"
    INTRO_HINT_CLASS = IntroHintFindContraversal
    DESCRIPTION_WIDGET_CLASS = FindContraversalDescriptionWidget
    ANSWER_WIDGET_CLASS = FindContraversalAnswerWidget

    def __init__(self, **kwargs):
        super(FindContraversal, self).__init__(**kwargs)
        self.point_count = None
        self.COLORS = {
            _("RED"): "#FF0000FF",
            _("BROWN"): "#D2691EFF",
            _("GREEN"): "#00FF00FF",
            _("BLUE"): "#0000FFFF",
            _("BLACK"): "#000000FF",
            _("PURPLE"): "#BA55D3FF"
        }

    def generate_alphabet(self):
        colors = list(self.COLORS.items())
        random.shuffle(colors)
        alphabet = colors[:self.SIZE]

        for i in xrange((self.SIZE - 1) * self.SIZE):
            name = random.choice(self.COLORS.keys())
            incorrect_colors = [value for value in self.COLORS.values() if value != self.COLORS[name]]
            alphabet.append(
                (name, random.choice(incorrect_colors))
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
        self.point_count = widget.add_variants(values, self._check_answer, right_colors=self.COLORS)
        return widget

    def on_correct_answer(self, button):
        App.get_running_app().sounds['success'].play()
        button.mark_correct()
        button.unbind(on_press=self._check_answer)
        self.num_succeed += 1

        if self.num_succeed >= self.point_count:
            self.finish()
