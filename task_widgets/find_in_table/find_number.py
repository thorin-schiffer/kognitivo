import string

from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .find_in_table import FindInTable

import_kv(__file__)


class IntroHintFindNumber(IntroHint):
    pass


class FindNumber(FindInTable):
    SIZE = 5
    TASK_KEY = "find_number"
    INTRO_HINT_CLASS = IntroHintFindNumber

    def generate_alphabet(self):
        return string.digits
