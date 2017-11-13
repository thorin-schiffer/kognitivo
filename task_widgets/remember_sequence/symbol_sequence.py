# -*- coding: utf-8 -*-
from answer_widgets import SymbolBoxAnswerWidget
from task_widgets.task_base.intro_hint import IntroHint
from utils import SYMBOLS_ALPHABET, import_kv, isp
from .remember_sequence import RememberSequence, RememberSequenceDescriptionWidget, \
    RememberSequenceHintWidget

import_kv(__file__)


class SymbolSequenceHintWidget(RememberSequenceHintWidget):
    pass


class SymbolSequenceDescriptionWidget(RememberSequenceDescriptionWidget):
    HINT_WIDGET_CLASS = SymbolSequenceHintWidget

    def __init__(self, **kwargs):
        super(SymbolSequenceDescriptionWidget, self).__init__(**kwargs)
        self.sequence_widget.font_name = "glyphicons"
        self.sequence_widget.font_size = isp(25)


class IntroHintSymbolSequence(IntroHint):
    pass


class SymbolSequence(RememberSequence):
    TASK_KEY = "symbol_sequence"
    INTRO_HINT_CLASS = IntroHintSymbolSequence
    DESCRIPTION_WIDGET_CLASS = SymbolSequenceDescriptionWidget
    ANSWER_WIDGET_CLASS = SymbolBoxAnswerWidget
    SIZE = 5
    TIME_PER_ELEMENT = 1

    def generate_alphabet(self):
        return SYMBOLS_ALPHABET
