import random

from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .calculation import ModeOperandsCalculation

import_kv(__file__)


class IntroHintNumbersCalculation(IntroHint):
    pass


class NumbersCalculation(ModeOperandsCalculation):
    FROM = 101
    TO = 899
    TASK_KEY = "numbers_calculation"
    INTRO_HINT_CLASS = IntroHintNumbersCalculation

    def calculate_operands(self):
        self.first = self.first or random.randint(self.FROM, self.TO - 100)
        self.result = self.result or random.randint(self.first + 100, self.TO)
        self.second = self.second or self.result - self.first

    def build_text(self):
        text = None
        if self.mode == 0:
            self.correct_answer = self.result
            text = "%s + %s = ?" % (self.first, self.second)

        if self.mode == 1:
            self.correct_answer = self.first
            text = "? + %s = %s" % (self.second, self.result)

        if self.mode == 2:
            self.correct_answer = self.second
            text = "%s + ? = %s" % (self.first, self.result)

        return text

    def get_next_variant(self):
        return self.correct_answer + 10 * random.randint(-10, +10)
