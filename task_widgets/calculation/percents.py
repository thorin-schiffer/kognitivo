# coding=utf-8
import random

from task_widgets.task_base.intro_hint import IntroHint
from utils import _
from utils import import_kv
from .calculation import OperandsCalculation

import_kv(__file__)


class IntroHintPercentsCalculation(IntroHint):
    pass


class PercentsCalculation(OperandsCalculation):
    FROM = 101
    TO = 999
    TASK_KEY = "percents_calculation"
    INTRO_HINT_CLASS = IntroHintPercentsCalculation
    EFFICIENCY_TO_POINTS = 20000

    def calculate_operands(self):
        self.first = random.randint(self.FROM, self.TO - 10)
        self.second = random.randint(10, 99)
        self.result = (self.first * self.second) / 100.

    def build_text(self):
        self.correct_answer = self.result
        text = _(u"%(percents)s%% of %(base)s?") % {
            "percents": self.second,
            "base": self.first
        }

        return text

    def get_next_variant(self):
        return self.correct_answer + random.randint(-100, +100)

    def variant_modifier(self, value):
        return "%.0f" % value
