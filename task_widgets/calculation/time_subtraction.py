from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .time_calculation import TimeCalculation

import_kv(__file__)


class IntroHintTimeSubtraction(IntroHint):
    pass


class TimeSubtraction(TimeCalculation):
    TASK_KEY = "time_subtraction"
    INTRO_HINT_CLASS = IntroHintTimeSubtraction
    EFFICIENCY_TO_POINTS = 20000

    def calculate_result(self):
        self.result = self.first - self.second
