import string
from kivy.app import App

from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .find_in_table_dynamic import FindInTableDynamic

import_kv(__file__)


class IntroHintFindLetterDynamic(IntroHint):
    pass


class FindLetterDynamic(FindInTableDynamic):
    SIZE = 5
    TASK_KEY = "find_letter_dynamic"
    INTRO_HINT_CLASS = IntroHintFindLetterDynamic

    def generate_alphabet(self):
        lang = App.get_running_app().lang
        return string.ascii_uppercase if lang != 'ru' else [unichr(i) for i in range(1040, 1072)]
