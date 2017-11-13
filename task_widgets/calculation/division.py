# coding=utf-8
import random

from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .calculation import ModeOperandsCalculation

import_kv(__file__)


class IntroHintDivisionCalculation(IntroHint):
    pass


class DivisionCalculation(ModeOperandsCalculation):
    FROM = 11
    TO = 99
    TASK_KEY = "division_calculation"
    INTRO_HINT_CLASS = IntroHintDivisionCalculation
    EFFICIENCY_TO_POINTS = 20000

    def calculate_operands(self):
        self.second = random.randint(self.FROM, self.TO - 10)
        self.result = random.randint(self.FROM, self.TO - 10)
        self.first = self.second * self.result

    def build_text(self):
        text = None
        if self.mode == 0:
            self.correct_answer = self.result
            text = u"%s ÷ %s = ?" % (self.first, self.second)

        if self.mode == 1:
            self.correct_answer = self.first
            text = u"? ÷ %s = %s" % (self.second, self.result)

        if self.mode == 2:
            self.correct_answer = self.second
            text = u"%s ÷ ? = %s" % (self.first, self.result)

        return text

    def get_next_variant(self):
        return self.correct_answer + random.randint(-10, +10)
