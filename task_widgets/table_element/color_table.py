from kivy.uix.label import Label
from kivy.utils import get_hex_from_color, get_color_from_hex

from kivy.properties import StringProperty

from answer_widgets import ColorTile, BoxButtonsAnswerWidget, ColorAnswerButton
from task_widgets.task_base.intro_hint import IntroHint
from utils import get_random_color, import_kv
from .table_element import TableElement, TableElementDescriptionWidget, TableCellMixin

import_kv(__file__)


class IntroHintColorTable(IntroHint):
    pass


class ColorTableTile(ColorTile, TableCellMixin):
    UNCHECKED_COLOR = get_color_from_hex("404087ff")
    text = StringProperty()

    def mark_point(self, *_):
        self.add_widget(Label(text="?", color=self.UNCHECKED_COLOR, font_size=self.font_size))


class ColorTableDescriptionWidget(TableElementDescriptionWidget):
    CELL_WIDGET = ColorTableTile

    def add_cell(self, value):
        self.table.add_widget(self.CELL_WIDGET(color=get_color_from_hex(value),
                                               text=value))


class ColorTableAnswerWidget(BoxButtonsAnswerWidget):
    BUTTON_WIDGET_CLASS = ColorAnswerButton


class ColorTable(TableElement):
    TASK_KEY = 'color_table'
    INTRO_HINT_CLASS = IntroHintColorTable
    DESCRIPTION_WIDGET_CLASS = ColorTableDescriptionWidget
    ANSWER_WIDGET_CLASS = ColorTableAnswerWidget

    def generate_alphabet(self):
        alphabet = []
        for i in xrange(self.SIZE ** 2):
            value = tuple(get_random_color())
            alphabet.append(get_hex_from_color(value))
        return alphabet
