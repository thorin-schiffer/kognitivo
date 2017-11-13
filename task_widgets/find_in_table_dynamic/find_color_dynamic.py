from kivy.utils import get_hex_from_color, get_color_from_hex

from answer_widgets import ColorAnswerButton
from task_widgets.find_in_table.find_color import ColorTableAnswerWidget
from task_widgets.task_base.intro_hint import IntroHint
from utils import get_random_color, import_kv
from .find_in_table_dynamic import FindInTableDynamic, \
    FindInTableDynamicAnswerWidget, \
    DynamicValueAnswerButton, FindInTableDynamicDescriptionWidget

import_kv(__file__)


class IntroHintFindColorDynamic(IntroHint):
    pass


class DynamicValueColorAnswerButton(ColorAnswerButton, DynamicValueAnswerButton):
    def set_value(self):
        self.inner_color = self.current_value if isinstance(self.current_value, (tuple, list)) else get_color_from_hex(
            self.current_value)

    def on_value(self, instance, value):
        self.select_random(instance, value)


class FindColorDynamicDescriptionWidget(FindInTableDynamicDescriptionWidget):
    pass


class FindColorDynamicAnswerWidget(FindInTableDynamicAnswerWidget, ColorTableAnswerWidget):
    BUTTON_WIDGET_CLASS = DynamicValueColorAnswerButton


class FindColorDynamic(FindInTableDynamic):
    SIZE = 5
    TASK_KEY = "find_color_dynamic"
    INTRO_HINT_CLASS = IntroHintFindColorDynamic
    ANSWER_WIDGET_CLASS = FindColorDynamicAnswerWidget
    DESCRIPTION_WIDGET_CLASS = FindColorDynamicDescriptionWidget

    def generate_alphabet(self):
        alphabet = []
        for i in xrange(self.SIZE):
            value = tuple(get_random_color())
            alphabet.append(get_hex_from_color(value))
        return alphabet
