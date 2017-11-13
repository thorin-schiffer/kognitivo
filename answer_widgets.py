from collections import defaultdict
from kivy.animation import Animation
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty

from settings import TEXT_COLOR
from library_widgets import AnimationMixin
from utils import import_kv

import_kv(__file__)


class AnswerButton(ButtonBehavior, Label):
    value = ObjectProperty()
    CORRECT_COLOR = get_color_from_hex("408742ff")
    INCORRECT_COLOR = get_color_from_hex("eb542cff")
    NOT_CHECKED_COLOR = TEXT_COLOR
    correctness_state = BooleanProperty(None, allownone=True)
    use_color = BooleanProperty(True)

    def mark_correct(self):
        if self.use_color:
            Animation(color=self.CORRECT_COLOR, duration=.5, t='in_out_cubic').start(self)
        self.correctness_state = True

    def mark_incorrect(self):
        if self.use_color:
            Animation(color=self.INCORRECT_COLOR, duration=.5, t='in_out_cubic').start(self)
        self.correctness_state = False
        original_y = self.y
        f_a = Animation(y=original_y + 10, duration=.1, t='out_circ')
        f_b = Animation(y=original_y - 10, duration=.1, t='out_circ')
        f_o = Animation(y=original_y, duration=.1, t='out_circ')
        animation = f_a + f_b + f_o
        animation.start(self)

    def un_check(self):
        if self.use_color:
            self.color = self.NOT_CHECKED_COLOR
        self.correctness_state = None


class BaseAnswerWidget(Widget):
    def get_values_widgets(self, *args, **kwargs):
        raise NotImplementedError("Implement in children")


class DisappearAnswerButton(AnswerButton, AnimationMixin):
    def __init__(self, **kwargs):
        super(DisappearAnswerButton, self).__init__(**kwargs)
        self.animation = Animation(opacity=0, y=0, t="in_out_cubic", duration=.5)


class DisappearOnCorrectAnswerButton(DisappearAnswerButton):
    def mark_correct(self):
        super(DisappearOnCorrectAnswerButton, self).mark_correct()
        self.animation.start(self)


class DisappearOnIncorrectAnswerButton(DisappearAnswerButton):
    def mark_incorrect(self):
        super(DisappearOnIncorrectAnswerButton, self).mark_incorrect()
        self.animation.start(self)


class ButtonsAnswerWidgetMixin(Widget):
    BUTTON_WIDGET_CLASS = AnswerButton
    buttons = ListProperty([])

    def add_variants(self, variants, callback, text_modifier=unicode):
        for variant in variants:
            button = self.BUTTON_WIDGET_CLASS(text=text_modifier(variant),
                                              value=variant,
                                              on_press=callback)
            self.buttons.append(button)
            self.add_widget(button)


class ButtonsAnswerWidget(ButtonsAnswerWidgetMixin, BaseAnswerWidget):
    def get_values_widgets(self, *args, **kwargs):
        result = defaultdict(list)
        for button in self.buttons:
            result[button.value].append(button)
        return result


class BoxButtonsAnswerWidget(BoxLayout, ButtonsAnswerWidget):
    pass


class TableButtonsAnswerWidget(GridLayout, ButtonsAnswerWidget):
    pass


class SymbolAnswerButton(AnswerButton):
    def __init__(self, **kwargs):
        super(SymbolAnswerButton, self).__init__(**kwargs)
        self.font_name = "glyphicons"
        self.markup = True


class DisappearingSymbolAnswerButton(DisappearOnCorrectAnswerButton):
    def __init__(self, **kwargs):
        super(DisappearingSymbolAnswerButton, self).__init__(**kwargs)
        self.font_name = "glyphicons"


class SymbolBoxAnswerWidget(BoxButtonsAnswerWidget):
    BUTTON_WIDGET_CLASS = DisappearingSymbolAnswerButton


class SymbolTableAnswerWidget(TableButtonsAnswerWidget):
    BUTTON_WIDGET_CLASS = DisappearingSymbolAnswerButton


class ColorTile(AnchorLayout):
    color = ListProperty((1, 1, 1, 1))


class BaseColorAnswerButton(AnchorLayout):
    inner_color = ListProperty((1, 1, 1, 1))
    NOT_CHECKED_COLOR = TEXT_COLOR

    def on_value(self, instance, value):
        instance.inner_color = value if isinstance(value, (tuple, list)) else get_color_from_hex(value)


class DisappearingOnCorrectColorAnswerButton(BaseColorAnswerButton, DisappearOnCorrectAnswerButton):
    pass


class DisappearingOnIncorrectColorAnswerButton(BaseColorAnswerButton, DisappearOnIncorrectAnswerButton):
    pass


class ColorAnswerButton(BaseColorAnswerButton, AnswerButton):
    pass
