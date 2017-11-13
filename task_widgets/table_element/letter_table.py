import string
from kivy.app import App

from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .table_element import TableElement

import_kv(__file__)


class IntroHintLetterTable(IntroHint):
    pass


class LetterTable(TableElement):
    TASK_KEY = 'letter_table'
    INTRO_HINT_CLASS = IntroHintLetterTable

    def generate_alphabet(self):
        lang = App.get_running_app().lang
        return string.ascii_uppercase if lang != 'ru' else [unichr(i) for i in range(1040, 1072)]
