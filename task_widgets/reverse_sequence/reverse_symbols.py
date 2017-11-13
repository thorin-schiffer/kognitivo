# coding=utf-8
from answer_widgets import SymbolBoxAnswerWidget, SymbolAnswerButton
from description_widgets import SymbolTextDescriptionWidget
from task_widgets.task_base.intro_hint import IntroHint
from utils import SYMBOLS_ALPHABET, import_kv
from .reverse_sequence import ReverseSequence

import_kv(__file__)


class IntroHintReverseSymbols(IntroHint):
    pass


class ReverseSymbolsAnswerWidget(SymbolBoxAnswerWidget):
    BUTTON_WIDGET_CLASS = SymbolAnswerButton


class ReverseSymbolsDescriptionWidget(SymbolTextDescriptionWidget):
    pass


class ReverseSymbols(ReverseSequence):
    TASK_KEY = "reverse_symbols"
    INTRO_HINT_CLASS = IntroHintReverseSymbols
    DESCRIPTION_WIDGET_CLASS = ReverseSymbolsDescriptionWidget
    ANSWER_WIDGET_CLASS = ReverseSymbolsAnswerWidget
    ANSWER_JOINER = u"[color=#ccccccff][font=RobotoCondensed]|[/font][/color]"

    def sequence_to_text(self):
        return u"[color=#ccccccff][font=RobotoCondensed]|[/font][/color]".join(self.sequence)

    def generate_alphabet(self):
        return SYMBOLS_ALPHABET
