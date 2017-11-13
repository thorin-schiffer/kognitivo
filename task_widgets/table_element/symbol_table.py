from kivy.animation import Animation

from answer_widgets import SymbolBoxAnswerWidget, SymbolAnswerButton
from task_widgets.task_base.intro_hint import IntroHint
from utils import SYMBOLS_ALPHABET, import_kv
from .table_element import TableElement, TableElementDescriptionWidget, TableCellWidget

import_kv(__file__)


class IntroHintSymbolTable(IntroHint):
    pass


class SymbolTableCell(TableCellWidget):
    def mark_point(self, *_):
        self.text = "[font=RobotoCondensed]?[/font]"
        self.color = self.UNCHECKED_COLOR
        Animation(opacity=1, d=.5, t='in_quad').start(self)

    def __init__(self, **kwargs):
        super(SymbolTableCell, self).__init__(**kwargs)
        self.markup = True
        self.font_name = 'glyphicons'
        self.animation = Animation(opacity=0, d=.5, t='in_quad')


class SymbolTableDescriptionWidget(TableElementDescriptionWidget):
    CELL_WIDGET = SymbolTableCell


class SymbolTableAnswerWidget(SymbolBoxAnswerWidget):
    BUTTON_WIDGET_CLASS = SymbolAnswerButton


class SymbolTable(TableElement):
    TASK_KEY = 'symbol_table'
    INTRO_HINT_CLASS = IntroHintSymbolTable
    DESCRIPTION_WIDGET_CLASS = SymbolTableDescriptionWidget
    ANSWER_WIDGET_CLASS = SymbolTableAnswerWidget

    def generate_alphabet(self):
        return SYMBOLS_ALPHABET
