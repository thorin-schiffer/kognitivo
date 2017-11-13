import random
from collections import defaultdict
from kivy.app import App
from kivy.clock import Clock

from kivy.properties import BooleanProperty, StringProperty, NumericProperty

from answer_widgets import DisappearOnCorrectAnswerButton, TableButtonsAnswerWidget
from description_widgets import TextDescriptionWidget
from task_widgets.find_in_table.find_in_table import FindInTable
from utils import import_kv

import_kv(__file__)


class DynamicValueAnswerButton(DisappearOnCorrectAnswerButton):
    to_randomize = BooleanProperty(True)
    current_value = StringProperty()
    iteration = NumericProperty(0)
    TIMEOUT_FROM = 1.0
    TIMEOUT_TO = 1.3

    def on_to_randomize(self, instance, value):
        if not value:
            Clock.unschedule(self.select_random)

    def set_value(self):
        self.text = self.current_value

    def select_random(self, *args, **kwargs):
        self.current_value = self.value[self.iteration % len(self.value)]
        self.iteration += 1

        self.set_value()
        if self.to_randomize:
            timeout = random.uniform(self.TIMEOUT_FROM,
                                     self.TIMEOUT_TO)
            Clock.schedule_once(self.select_random, timeout=timeout)

    on_value = select_random


class FindInTableDynamicDescriptionWidget(TextDescriptionWidget):
    pattern = StringProperty()


class FindInTableDynamicAnswerWidget(TableButtonsAnswerWidget):
    BUTTON_WIDGET_CLASS = DynamicValueAnswerButton

    def get_values_widgets(self, *args, **kwargs):
        result = defaultdict(list)
        for button in self.buttons:
            result[button.current_value].append(button)
        return result

    def disable_randomization(self):
        for button in self.buttons:
            button.to_randomize = False


class FindInTableDynamic(FindInTable):
    ANSWER_WIDGET_CLASS = FindInTableDynamicAnswerWidget
    DESCRIPTION_WIDGET_CLASS = FindInTableDynamicDescriptionWidget

    def get_answer_widget(self):

        values = []
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                values.append(self.point_set[j:] + self.point_set[:j])
        random.shuffle(values)
        widget = super(FindInTable, self).get_answer_widget(rows=self.SIZE, cols=self.SIZE)
        widget.add_variants(values, self._check_answer, lambda x: "?")
        return widget

    def _check_answer(self, widget):
        if self.correct_answer is None:
            raise ValueError("Task.correct_answer should be set")

        if not self.successful:
            value = widget.current_value

            if value == self.correct_answer:
                self.on_correct_answer(widget)
            else:
                self.on_incorrect_answer(widget)

    def on_incorrect_answer(self, button):
        App.get_running_app().sounds['fail'].play()
        from managers.vibration import vibration_manager
        vibration_manager.vibrate(100)

        button.mark_incorrect()
        self.mistakes_count += 1

    def finish(self, update_status=True):
        self.answer_widget.disable_randomization()
        super(FindInTableDynamic, self).finish(update_status)
