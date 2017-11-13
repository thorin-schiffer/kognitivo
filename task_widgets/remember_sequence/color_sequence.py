from kivy.uix.boxlayout import BoxLayout

from answer_widgets import BoxButtonsAnswerWidget, DisappearingOnCorrectColorAnswerButton, ColorTile
from task_widgets.task_base.intro_hint import IntroHint
from utils import get_random_color, import_kv
from .remember_sequence import RememberSequence, RememberSequenceDescriptionWidget, \
    RememberSequenceHintWidget

import_kv(__file__)


class ColorSequenceHintWidget(RememberSequenceHintWidget):
    pass


class ColorSequenceSequenceWidget(BoxLayout):
    pass


class ColorSequenceDescriptionWidget(RememberSequenceDescriptionWidget):
    HINT_WIDGET_CLASS = ColorSequenceHintWidget
    SEQUENCE_WIDGET_CLASS = ColorSequenceSequenceWidget


class IntroHintColorSequence(IntroHint):
    pass


class ColorSequenceAnswerWidget(BoxButtonsAnswerWidget):
    BUTTON_WIDGET_CLASS = DisappearingOnCorrectColorAnswerButton


class ColorSequence(RememberSequence):
    TASK_KEY = "color_sequence"
    INTRO_HINT_CLASS = IntroHintColorSequence
    DESCRIPTION_WIDGET_CLASS = ColorSequenceDescriptionWidget
    ANSWER_WIDGET_CLASS = ColorSequenceAnswerWidget
    TIME_PER_ELEMENT = 1
    SIZE = 5
    NOT_CHECKED_COLOR = (1, 1, 1, 1)

    def get_description_widget(self):
        widget = self.DESCRIPTION_WIDGET_CLASS()
        for i in xrange(self.SIZE):
            value = tuple(get_random_color())
            self.sequence.append(value)
            widget.sequence_widget.add_widget(ColorTile(color=value))
        return widget
