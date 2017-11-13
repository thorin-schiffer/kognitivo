from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

from utils import import_kv

import_kv(__file__)


class IntroHint(BoxLayout):
    title = StringProperty()
    title_label = ObjectProperty()

    description = StringProperty()
    description_label = ObjectProperty()

    icon = StringProperty()
    icon_image = ObjectProperty()

    indicator_panel = ObjectProperty()
    task = ObjectProperty()

    tutorial = ObjectProperty()

    def start_immediately(self):
        self.task.start()

    def on_title(self, _, value):
        if self.title_label is not None:
            self.title_label.text = value

    def on_description(self, _, value):
        if self.description_label is not None:
            self.description_label.text = value

    def on_icon(self, _, value):
        if self.icon_image is not None:
            self.icon_image.source = value

    def __init__(self, **kwargs):
        self.start = None
        super(IntroHint, self).__init__(**kwargs)
        self.bind(title=self.on_title,
                  description=self.on_description,
                  icon=self.on_icon)

    def on_parent(self, instance, value):
        if value is None:
            self.tutorial.stop()


class StartTestButton(ButtonBehavior, AnchorLayout):
    intro = ObjectProperty()
    started = BooleanProperty(False)

    def fill_canvas(self):
        from kivy.graphics import Ellipse, Color
        from settings import FILL_COLOR
        with self.canvas.before:
            self._color = Color(*FILL_COLOR)
            self._ellipse = Ellipse()

    def on_size_pos(self, instance, _):
        d = min(self.size)
        pos = (self.pos[0] + self.size[0] / 2 - d / 2,
               self.pos[1] + self.size[1] / 2 - d / 2)
        self._ellipse.size = (d, d)
        self._ellipse.pos = pos

    on_size = on_pos = on_size_pos

    def on_press(self, *_):
        if not self.started:
            self.intro.start_immediately()
            self.started = True

    def __init__(self, **kwargs):
        self._color = None
        self._ellipse = None
        super(StartTestButton, self).__init__(**kwargs)
        self.fill_canvas()
