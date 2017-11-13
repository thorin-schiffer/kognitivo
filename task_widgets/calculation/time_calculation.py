import random
from datetime import timedelta

from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .time_base import TimeCalculationBase

import_kv(__file__)


class IntroHintTimeCalculation(IntroHint):
    pass


class TimeCalculation(TimeCalculationBase):
    TASK_KEY = "time_calculation"
    INTRO_HINT_CLASS = IntroHintTimeCalculation

    def calculate_result(self):
        self.result = self.first + self.second

    def get_next_variant(self):
        return self.correct_answer + timedelta(hours=0, minutes=10 * random.randint(-5, 5))

    def variant_modifier(self, value):
        return value.strftime("%H:%M")
