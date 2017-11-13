from kivy.properties import StringProperty

from answer_widgets import SymbolTableAnswerWidget
from task_widgets.task_base.intro_hint import IntroHint
from utils import SYMBOLS_ALPHABET, import_kv
from .find_in_table import FindInTable, FindInTableDescriptionWidget

import_kv(__file__)


class IntroHintFindSymbol(IntroHint):
    pass


class FindSymbolDescriptionWidget(FindInTableDescriptionWidget):
    pattern = StringProperty()


class FindSymbol(FindInTable):
    SIZE = 5
    TASK_KEY = "find_symbol"
    INTRO_HINT_CLASS = IntroHintFindSymbol
    DESCRIPTION_WIDGET_CLASS = FindSymbolDescriptionWidget
    ANSWER_WIDGET_CLASS = SymbolTableAnswerWidget

    def generate_alphabet(self):
        return SYMBOLS_ALPHABET
