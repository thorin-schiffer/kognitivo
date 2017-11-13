from answer_widgets import SymbolTableAnswerWidget, SymbolAnswerButton
from task_widgets.task_base.intro_hint import IntroHint
from utils import SYMBOLS_ALPHABET, import_kv
from .find_in_table_dynamic import FindInTableDynamic, \
    FindInTableDynamicAnswerWidget, \
    DynamicValueAnswerButton, FindInTableDynamicDescriptionWidget

import_kv(__file__)


class IntroHintFindSymbolDynamic(IntroHint):
    pass


class DynamicValueSymbolAnswerButton(SymbolAnswerButton, DynamicValueAnswerButton):
    pass


class FindSymbolDynamicDescriptionWidget(FindInTableDynamicDescriptionWidget):
    pass


class FindSymbolDynamicAnswerWidget(FindInTableDynamicAnswerWidget, SymbolTableAnswerWidget):
    BUTTON_WIDGET_CLASS = DynamicValueSymbolAnswerButton


class FindSymbolDynamic(FindInTableDynamic):
    SIZE = 5
    TASK_KEY = "find_symbol_dynamic"
    INTRO_HINT_CLASS = IntroHintFindSymbolDynamic
    ANSWER_WIDGET_CLASS = FindSymbolDynamicAnswerWidget
    DESCRIPTION_WIDGET_CLASS = FindSymbolDynamicDescriptionWidget

    def generate_alphabet(self):
        return SYMBOLS_ALPHABET
