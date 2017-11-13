import random
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty
from task_widgets.task_base.mixins import StartOnTimeoutMixin

from answer_widgets import BoxButtonsAnswerWidget
from description_widgets import BaseDescriptionWidget
from library_widgets import AnimationMixin
from task_widgets.task_base.base import BaseTask
from utils import import_kv

import_kv(__file__)


class TableCellMixin(Widget):
    def hide_content(self, mark):
        if mark:
            self.animation.bind(on_complete=self.mark_point)
        self.animation.start(self)

    def mark_point(self, *_):
        self.text = "?"
        Animation(opacity=1, d=.5, t='in_quad').start(self)


class TableCellWidget(TableCellMixin, Label, AnimationMixin):
    UNCHECKED_COLOR = get_color_from_hex("404087ff")


class TableElementDescriptionWidget(BoxLayout, BaseDescriptionWidget):
    table = ObjectProperty()
    table_size = NumericProperty()
    CELL_WIDGET = TableCellWidget
    hidden = BooleanProperty(False)

    def hide_contents(self, correct_answer):
        self.hidden = True
        for cell in self.table.children:
            cell.hide_content(cell.text == correct_answer)

    def add_cell(self, value):
        self.table.add_widget(self.CELL_WIDGET(text=value))


class TableElement(BaseTask, StartOnTimeoutMixin):
    DESCRIPTION_WIDGET_CLASS = TableElementDescriptionWidget
    ANSWER_WIDGET_CLASS = BoxButtonsAnswerWidget
    SIZE = 3
    SHOW_TIME = 3

    def __init__(self, **kwargs):
        super(TableElement, self).__init__(**kwargs)
        self.point_set = []
        self.variants = []

    def generate_alphabet(self):
        raise NotImplementedError()

    def get_description_widget(self, **kwargs):
        widget = super(TableElement, self).get_description_widget(table_size=self.SIZE)
        values = list(self.generate_alphabet())
        random.shuffle(values)
        for i in xrange(self.SIZE ** 2):
            value = values[i]
            self.point_set.append(value)
            widget.add_cell(value)
        return widget

    def get_variants(self):
        variants = list(set(self.point_set))
        random.shuffle(variants)
        self.variants = variants[:self.SIZE]
        self.correct_answer = random.choice(self.variants)

    def get_answer_widget(self, **kwargs):
        widget = super(TableElement, self).get_answer_widget(**kwargs)
        widget.add_variants(self.variants, self._check_answer)
        return widget

    def add_main_widgets(self):
        pass

    def on_intro_hint_hide(self):
        self.description_widget = self.get_description_widget()
        self.main_area.add_widget(self.description_widget)

    def on_timeout(self, *args, **kwargs):
        StartOnTimeoutMixin.on_timeout(self, *args, **kwargs)
        self.get_variants()
        self.description_widget.hide_contents(self.correct_answer)
        self.main_area.add_widget(self.get_answer_widget())
