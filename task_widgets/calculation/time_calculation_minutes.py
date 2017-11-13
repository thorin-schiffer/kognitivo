from kivy.uix.boxlayout import BoxLayout

from kivy.properties import ObjectProperty

from description_widgets import BaseDescriptionWidget
from task_widgets.task_base.intro_hint import IntroHint
from utils import _, import_kv
from .time_base import IntervalClock
from .time_calculation import TimeCalculation

import_kv(__file__)


class MinutesIntervalClock(IntervalClock):
    PATTERN = u"%d %s"

    def update_label(self, instance, *args):
        if self.label is not None:
            self.label.text = self.PATTERN % (
                self.hour * 60 + self.minute,
                _("min.")
            )
        self.hour_angle = (self.hour + self.minute / 60.) * 30

    on_hour = on_minute = on_label = update_label


class IntroHintTimeCalculationMinutes(IntroHint):
    pass


class TimeCalculationMinutesDescriptionWidget(BoxLayout, BaseDescriptionWidget):
    left_clock = ObjectProperty()
    right_clock = ObjectProperty()


class TimeCalculationMinutes(TimeCalculation):
    TASK_KEY = "time_calculation_minutes"
    INTRO_HINT_CLASS = IntroHintTimeCalculationMinutes
    DESCRIPTION_WIDGET_CLASS = TimeCalculationMinutesDescriptionWidget
    EFFICIENCY_TO_POINTS = 20000
