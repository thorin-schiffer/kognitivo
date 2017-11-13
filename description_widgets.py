from kivy.uix.label import Label
from kivy.uix.widget import Widget
from utils import import_kv

import_kv(__file__)


class BaseDescriptionWidget(Widget):
    pass


class TextDescriptionWidget(Label, BaseDescriptionWidget):
    pass


class SymbolTextDescriptionWidget(Label, BaseDescriptionWidget):
    def __init__(self, **kwargs):
        super(SymbolTextDescriptionWidget, self).__init__(**kwargs)
        self.font_name = "glyphicons"
