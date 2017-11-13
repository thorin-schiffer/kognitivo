# -*- coding: utf-8 -*-
import random
from kivy.app import App

from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .find_in_table import FindInTable, FindInTableDescriptionWidget, FindInTableAnswerWidget

import_kv(__file__)


class IntroHintFindPrimer(IntroHint):
    pass


class FindPrimerDescriptionWidget(FindInTableDescriptionWidget):
    pass


class FindPrimerAnswerWidget(FindInTableAnswerWidget):
    def add_variants(self, variants, callback, text_modifier=unicode):
        i = 0
        size = len(variants) / 2
        right_answers = range(size ** 2)
        random.shuffle(right_answers)
        right_answers = right_answers[:size]
        for first in variants[:size]:
            for second in variants[size:]:
                if i in right_answers:
                    if i % 2:
                        text = "%s+%s=%s" % (first, second, first + second)
                    else:
                        mx = max(first, second)
                        mn = min(first, second)
                        text = "%s-%s=%s" % (mx, mn, mx - mn)
                    value = True
                else:
                    if i % 2:
                        text = "%s+%s=%s" % (first, second, first + second + random.randint(10, 20))
                    else:
                        mx = max(first, second)
                        mn = min(first, second)
                        text = "%s-%s=%s" % (mx, mn, mx - mn + random.randint(10, 20))
                    value = False

                button = self.BUTTON_WIDGET_CLASS(text=text,
                                                  value=value,
                                                  on_press=callback)
                self.buttons.append(button)
                self.add_widget(button)
                i += 1

        return size


class FindPrimer(FindInTable):
    SIZE = 3
    TASK_KEY = "find_primer"
    INTRO_HINT_CLASS = IntroHintFindPrimer
    DESCRIPTION_WIDGET_CLASS = FindPrimerDescriptionWidget
    ANSWER_WIDGET_CLASS = FindPrimerAnswerWidget
    FROM = 10
    TO = 99
    EFFICIENCY_TO_POINTS = 20000

    def __init__(self, **kwargs):
        super(FindPrimer, self).__init__(**kwargs)
        self.point_count = None

    def generate_alphabet(self):
        return [random.randint(self.FROM, self.TO) for i in xrange(self.SIZE * 2)]

    def get_description_widget(self, **kwargs):
        self.correct_answer = True
        widget = super(FindInTable, self).get_description_widget(**kwargs)
        return widget

    def get_answer_widget(self):
        values = self.generate_alphabet()
        widget = super(FindInTable, self).get_answer_widget(rows=self.SIZE, cols=self.SIZE)
        self.point_count = widget.add_variants(values, self._check_answer)
        return widget

    def on_correct_answer(self, button):
        App.get_running_app().sounds['success'].play()
        button.mark_correct()
        button.unbind(on_press=self._check_answer)
        self.num_succeed += 1

        if self.num_succeed >= self.point_count:
            self.finish()
