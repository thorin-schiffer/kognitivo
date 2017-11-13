import string

from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .remember_sequence import RememberSequenceHintWidget, RememberSequenceDescriptionWidget, \
    RememberSequence

import_kv(__file__)


class NumberSequenceHintWidget(RememberSequenceHintWidget):
    pass


class NumberSequenceDescriptionWidget(RememberSequenceDescriptionWidget):
    HINT_WIDGET_CLASS = NumberSequenceHintWidget


class IntroHintNumberSequence(IntroHint):
    pass


class NumberSequence(RememberSequence):
    TASK_KEY = "number_sequence"
    INTRO_HINT_CLASS = IntroHintNumberSequence
    DESCRIPTION_WIDGET_CLASS = NumberSequenceDescriptionWidget
    SIZE = 5

    def generate_alphabet(self):
        return string.digits
