import string
from kivy.app import App

from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .reverse_sequence import ReverseSequence

import_kv(__file__)


class IntroHintReverseLetters(IntroHint):
    pass


class ReverseLetters(ReverseSequence):
    TASK_KEY = "reverse_letters"
    INTRO_HINT_CLASS = IntroHintReverseLetters

    def generate_alphabet(self):
        lang = App.get_running_app().lang
        return string.ascii_uppercase if lang != 'ru' else [unichr(i) for i in range(1040, 1072)]
