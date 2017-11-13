import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from kivy.properties import ObjectProperty, StringProperty
from task_widgets.task_base.mixins import StartOnTimeoutMixin

from answer_widgets import BoxButtonsAnswerWidget, DisappearOnCorrectAnswerButton
from description_widgets import BaseDescriptionWidget
from task_widgets.task_base.base import BaseTask
from utils import import_kv

import_kv(__file__)


class RememberSequenceSequenceWidget(Label):
    pass


class RememberSequenceHintWidget(Label):
    pass


class RememberSequenceDescriptionWidget(BoxLayout, BaseDescriptionWidget):
    HINT_WIDGET_CLASS = RememberSequenceHintWidget
    SEQUENCE_WIDGET_CLASS = RememberSequenceSequenceWidget

    hint_widget = ObjectProperty()
    sequence_widget = ObjectProperty()
    remain_bar = ObjectProperty()
    text_after_hide = StringProperty()

    def __init__(self, **kwargs):
        super(RememberSequenceDescriptionWidget, self).__init__(**kwargs)
        self.hint_widget = self.HINT_WIDGET_CLASS()
        self.add_widget(self.hint_widget)
        self.sequence_widget = self.SEQUENCE_WIDGET_CLASS()
        self.add_widget(self.sequence_widget)

    def hide_sequence(self):
        self.remove_widget(self.sequence_widget)
        self.hint_widget.text = self.text_after_hide


class RememberSequenceAnswerWidget(BoxButtonsAnswerWidget):
    BUTTON_WIDGET_CLASS = DisappearOnCorrectAnswerButton


class RememberSequence(BaseTask, StartOnTimeoutMixin):
    DESCRIPTION_WIDGET_CLASS = RememberSequenceDescriptionWidget
    ANSWER_WIDGET_CLASS = RememberSequenceAnswerWidget
    TIME_PER_ELEMENT = 0.2

    def __init__(self, **kwargs):
        self.sequence = []
        self.buttons = []
        self.current_sequence_index = 0

        BaseTask.__init__(self, **kwargs)
        self.SHOW_TIME = self.TIME_PER_ELEMENT * self.SIZE

    def generate_alphabet(self):
        raise NotImplementedError()

    def get_description_widget(self):
        for _ in xrange(self.SIZE):
            self.sequence.append(random.choice(self.generate_alphabet()))
        widget = self.DESCRIPTION_WIDGET_CLASS()
        widget.sequence_widget.text = " ".join(self.sequence)
        return widget

    def get_answer_widget(self):

        variants = list(self.sequence)
        random.shuffle(variants)
        container = super(RememberSequence, self).get_answer_widget()
        container.add_variants(variants, self._check_answer)
        return container

    def on_timeout(self, *args, **kwargs):
        StartOnTimeoutMixin.on_timeout(self, *args, **kwargs)
        self.description_widget.hide_sequence()
        self.main_area.add_widget(self.get_answer_widget())
        self.correct_answer = self.sequence[self.current_sequence_index]

    # overload adding widgets and start logics
    def add_main_widgets(self):
        pass

    def on_intro_hint_hide(self):
        self.description_widget = self.get_description_widget()
        self.main_area.add_widget(self.description_widget)

    def _reset_buttons(self):
        for button in self.buttons:
            if button.correctness_state is False:
                button.un_check()

    def on_incorrect_answer(self, button):
        App.get_running_app().sounds['fail'].play()
        from managers.vibration import vibration_manager
        vibration_manager.vibrate(100)

        button.mark_incorrect()
        self.mistakes_count += 1

    def on_correct_answer(self, button):
        App.get_running_app().sounds['success'].play()
        button.mark_correct()
        button.unbind(on_press=self._check_answer)
        self.num_succeed += 1
        # if last letter
        if self.current_sequence_index == self.SIZE - 1:
            self.finish()
        else:
            self._reset_buttons()
            self.current_sequence_index += 1
            self.correct_answer = self.sequence[self.current_sequence_index]
