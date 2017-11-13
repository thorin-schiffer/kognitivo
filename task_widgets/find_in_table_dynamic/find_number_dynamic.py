import string

from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .find_in_table_dynamic import FindInTableDynamic

import_kv(__file__)


class IntroHintFindNumberDynamic(IntroHint):
    pass


class FindNumberDynamic(FindInTableDynamic):
    SIZE = 5
    TASK_KEY = "find_number_dynamic"
    INTRO_HINT_CLASS = IntroHintFindNumberDynamic

    def generate_alphabet(self):
        return tuple(string.digits)
