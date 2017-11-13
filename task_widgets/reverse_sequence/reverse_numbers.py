import string

from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .reverse_sequence import ReverseSequence

import_kv(__file__)


class IntroHintReverseNumbers(IntroHint):
    pass


class ReverseNumbers(ReverseSequence):
    TASK_KEY = "reverse_numbers"
    INTRO_HINT_CLASS = IntroHintReverseNumbers

    def generate_alphabet(self):
        return string.digits
