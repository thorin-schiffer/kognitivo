import string
from kivy.app import App

from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .remember_sequence import RememberSequence, RememberSequenceDescriptionWidget, \
    RememberSequenceHintWidget

import_kv(__file__)


class LetterSequenceHintWidget(RememberSequenceHintWidget):
    pass


class LetterSequenceDescriptionWidget(RememberSequenceDescriptionWidget):
    HINT_WIDGET_CLASS = LetterSequenceHintWidget


class IntroHintLetterSequence(IntroHint):
    pass


class LetterSequence(RememberSequence):
    TASK_KEY = "letter_sequence"
    INTRO_HINT_CLASS = IntroHintLetterSequence
    DESCRIPTION_WIDGET_CLASS = LetterSequenceDescriptionWidget
    SIZE = 5

    def generate_alphabet(self):
        lang = App.get_running_app().lang
        return string.ascii_lowercase if lang != 'ru' else [unichr(i) for i in range(1040, 1072)]
