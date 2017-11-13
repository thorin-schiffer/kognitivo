import string

from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .table_element import TableElement

import_kv(__file__)


class IntroHintNumberTable(IntroHint):
    pass


class NumberTable(TableElement):
    TASK_KEY = 'number_table'
    INTRO_HINT_CLASS = IntroHintNumberTable

    def generate_alphabet(self):
        return string.digits
