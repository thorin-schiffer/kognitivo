import random
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from .calculation import OperandsCalculation
from description_widgets import BaseDescriptionWidget
from utils import import_kv
from datetime import datetime, timedelta

import_kv(__file__)


class Clock(BoxLayout):
    hour = NumericProperty()
    minute = NumericProperty()
    label = ObjectProperty()
    hour_angle = NumericProperty()
    minute_angle = NumericProperty()
    PATTERN = "%02d:%02d"

    def update_label(self, instance, _):
        self.hour_angle = -(self.hour + self.minute / 60.) * 30
        self.minute_angle = -self.minute * 6

        if self.label is not None:
            self.label.text = self.PATTERN % (self.hour, self.minute)

    on_hour = on_minute = on_label = update_label


class IntervalClock(Clock):
    PATTERN = "%d h %d m"

    def update_label(self, *args):
        super(IntervalClock, self).update_label(*args)
        self.hour_angle = (self.hour + self.minute / 60.) * 30


class TimeCalculationDescriptionWidget(BoxLayout, BaseDescriptionWidget):
    left_clock = ObjectProperty()
    right_clock = ObjectProperty()


class TimeCalculationBase(OperandsCalculation):
    DESCRIPTION_WIDGET_CLASS = TimeCalculationDescriptionWidget
    from_time = ObjectProperty(None, allownone=True)
    interval = ObjectProperty(None, allownone=True)

    FROM = 0
    TO = 5

    def calculate_result(self):
        raise NotImplementedError()

    def calculate_operands(self):
        self.first = self.first or datetime(2000, 1, 1,
                                            hour=random.randint(self.FROM, self.TO),
                                            minute=random.randint(0, 59))
        self.second = self.second or timedelta(hours=random.randint(self.FROM + 1, self.TO),
                                               minutes=random.randint(0, 59))
        self.calculate_result()

    def get_description_widget(self, **kwargs):
        widget = super(OperandsCalculation, self).get_description_widget(**kwargs)
        widget.left_clock.hour = self.first.hour
        widget.left_clock.minute = self.first.minute

        widget.right_clock.hour = self.second.seconds / 3600
        widget.right_clock.minute = (self.second.seconds - widget.right_clock.hour * 3600) / 60
        self.correct_answer = self.result
        return widget
