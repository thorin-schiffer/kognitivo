import random
from kivy.app import App

from kivy.properties import StringProperty
from task_widgets.task_base.mixins import StartImmediatelyMixin

from answer_widgets import TableButtonsAnswerWidget, DisappearOnCorrectAnswerButton
from description_widgets import TextDescriptionWidget
from task_widgets.task_base.base import BaseTask
from utils import import_kv

import_kv(__file__)


class FindInTableDescriptionWidget(TextDescriptionWidget):
    pattern = StringProperty()


class FindInTableAnswerWidget(TableButtonsAnswerWidget):
    BUTTON_WIDGET_CLASS = DisappearOnCorrectAnswerButton


class FindInTable(BaseTask, StartImmediatelyMixin):
    SIZE = 5
    ANSWER_WIDGET_CLASS = FindInTableAnswerWidget
    DESCRIPTION_WIDGET_CLASS = FindInTableDescriptionWidget

    def __init__(self, **kwargs):
        self.point_set = tuple()
        super(FindInTable, self).__init__(**kwargs)

    def generate_alphabet(self):
        raise NotImplementedError()

    def get_description_widget(self, **kwargs):
        alpha = list(self.generate_alphabet())
        random.shuffle(alpha)
        self.point_set = tuple(alpha[:self.SIZE])
        self.correct_answer = random.choice(self.point_set)
        widget = super(FindInTable, self).get_description_widget(**kwargs)
        widget.text = widget.pattern % self.correct_answer.upper()
        return widget

    def get_answer_widget(self):
        values = list(self.point_set * self.SIZE)
        random.shuffle(values)
        widget = super(FindInTable, self).get_answer_widget(rows=self.SIZE, cols=self.SIZE)
        widget.add_variants(values, self._check_answer)
        return widget

    def on_correct_answer(self, button):
        App.get_running_app().sounds['success'].play()
        button.mark_correct()
        button.unbind(on_press=self._check_answer)
        self.num_succeed += 1

        if self.num_succeed == self.SIZE:
            self.finish()
