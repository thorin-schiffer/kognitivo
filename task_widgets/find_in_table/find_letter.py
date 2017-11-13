import string
from kivy.app import App

from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .find_in_table import FindInTable

import_kv(__file__)


class IntroHintFindLetter(IntroHint):
    pass


class FindLetter(FindInTable):
    SIZE = 5
    TASK_KEY = "find_letter"
    INTRO_HINT_CLASS = IntroHintFindLetter

    def generate_alphabet(self):
        lang = App.get_running_app().lang
        return string.ascii_uppercase if lang != 'ru' else [unichr(i) for i in range(1040, 1072)]
