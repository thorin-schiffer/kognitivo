from kivy.properties import StringProperty

from answer_widgets import TableButtonsAnswerWidget, DisappearingOnCorrectColorAnswerButton
from task_widgets.task_base.intro_hint import IntroHint
from utils import import_kv
from .find_in_table import FindInTable, FindInTableDescriptionWidget

import_kv(__file__)


class IntroHintFindColor(IntroHint):
    pass


class FindColorDescriptionWidget(FindInTableDescriptionWidget):
    pattern = StringProperty()


class ColorTableAnswerWidget(TableButtonsAnswerWidget):
    BUTTON_WIDGET_CLASS = DisappearingOnCorrectColorAnswerButton


class FindColor(FindInTable):
    SIZE = 5
    TASK_KEY = "find_color"
    INTRO_HINT_CLASS = IntroHintFindColor
    DESCRIPTION_WIDGET_CLASS = FindColorDescriptionWidget
    ANSWER_WIDGET_CLASS = ColorTableAnswerWidget

    def generate_alphabet(self):
        from kivy.utils import get_hex_from_color
        from utils import get_random_color

        alphabet = []
        for i in xrange(self.SIZE):
            value = tuple(get_random_color())
            alphabet.append(get_hex_from_color(value))
        return alphabet
