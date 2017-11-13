# -*- coding: utf-8 -*-
from kivy.animation import Animation
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty, StringProperty, DictProperty, ObjectProperty
from kivy.logger import Logger

from utils import _, popup_open


class DiagramXLabel(Label):
    pass


class DiagramElementsContainer(Widget):
    values = ListProperty()
    color = ListProperty()
    LABEL_SIZE = dp(100)

    def on_color(self, instance, value):
        if self.fill_color:
            Animation(rgba=value, duration=.5, t='in_out_cubic').start(self.fill_color)

    def __init__(self, **kwargs):
        self.fill_color = None
        self.normal_level_line = None
        self.normal_level_label = None
        self.half_level_line = None
        self.half_level_label = None
        super(DiagramElementsContainer, self).__init__(**kwargs)
        self.bind(values=self.update_elements,
                  pos=self.update_elements,
                  width=self.update_elements,
                  height=self.update_elements)

    def fill_canvas(self):
        from kivy.graphics.context_instructions import Color
        from kivy.graphics.vertex_instructions import Line

        self.normal_level_label = Label(text="100% ",
                                        bold=True,
                                        halign='right',
                                        valign='bottom',
                                        size=(self.LABEL_SIZE, self.LABEL_SIZE),
                                        text_size=(self.LABEL_SIZE, self.LABEL_SIZE))

        self.half_level_label = Label(text="50% ",
                                      bold=True,
                                      halign='right',
                                      valign='bottom',
                                      size=(self.LABEL_SIZE, self.LABEL_SIZE),
                                      text_size=(self.LABEL_SIZE, self.LABEL_SIZE))

        self.add_widget(self.normal_level_label)
        self.add_widget(self.half_level_label)

        with self.canvas.before:
            self.fill_color = Color()

        with self.canvas.after:
            Color(1, 1, 1, 1)
            self.normal_level_line = Line(width=dp(2))
            self.half_level_line = Line(width=dp(2))

    def update_elements(self, *args, **kwargs):
        if not self.values:
            return
        if not self.fill_color:
            self.fill_canvas()
        max_y = float(max(self.values))

        if max_y < 0.01:
            return

        normal_level_height = self.height * (1. / max_y)
        half_level_height = self.height * (.5 / max_y)
        normal_level_y = self.y + normal_level_height
        half_level_y = self.y + half_level_height

        if normal_level_height > self.height:
            if App.get_running_app().root_window:
                normal_level_y = App.get_running_app().root_window.height

        if half_level_height > self.height:
            if App.get_running_app().root_window:
                half_level_y = App.get_running_app().root_window.height

        self.normal_level_line.points = (self.x, normal_level_y, self.x + self.width, normal_level_y)
        self.normal_level_label.pos = (self.x + self.width - self.LABEL_SIZE, normal_level_y)

        self.half_level_line.points = (self.x, half_level_y, self.x + self.width, half_level_y)
        self.half_level_label.pos = (self.x + self.width - self.LABEL_SIZE, half_level_y)


class DiagramLabelsContainer(BoxLayout):
    values = ListProperty()

    def on_values(self, instance, values):
        self.clear_widgets()
        for value in values:
            label = DiagramXLabel(text=self.format_x_label(value))
            self.add_widget(label)

    def format_x_label(self, value):
        return unicode(value)


class FilledLineDiagramElementsContainer(DiagramElementsContainer):
    def update_elements(self, *args, **kwargs):
        super(FilledLineDiagramElementsContainer, self).update_elements(*args, **kwargs)
        if not self.values or not self.quads:
            Logger.info("Diagram: values are empty, won't locate quads")
            return
        if not (len(self.values) - 1):
            width = self.width
        else:
            width = self.width / (len(self.values) - 1)
        max_y = float(max(self.values))
        if max_y < 0.01:
            return

        for i in range(len(self.values) - 1):
            x1 = self.x + width * i
            y1 = self.y
            x2 = x1
            h1 = self.height * (self.values[i] / max_y)
            if h1 < 0:
                h1 = 0
            y2 = y1 + h1

            x3 = self.x + width * (i + 1)
            h2 = self.height * (self.values[i + 1] / max_y)
            if h2 < 0:
                h2 = 0
            y3 = y1 + h2
            x4 = x3
            y4 = y1
            self.quads[i].points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def fill_canvas(self):
        super(FilledLineDiagramElementsContainer, self).fill_canvas()
        from kivy.graphics.vertex_instructions import Quad

        self.quads = []
        with self.canvas.before:
            self.quads = [Quad() for i in range(len(self.values) - 1)]

    def __init__(self, **kwargs):
        super(FilledLineDiagramElementsContainer, self).__init__(**kwargs)
        self.quads = None


class Diagram(BoxLayout):
    values = DictProperty()

    labels_container = ObjectProperty()
    elements_container = ObjectProperty()
    color = ListProperty()

    def on_color(self, instance, value):
        self.elements_container.color = value

    def on_values(self, instance, values):
        keys = list(values.keys())
        keys.sort()
        self.labels_container.values = keys
        self.elements_container.values = [values[key] for key in keys]


class BarDiagramElementsContainer(DiagramElementsContainer):
    spacing = NumericProperty()

    def fill_canvas(self):
        super(BarDiagramElementsContainer, self).fill_canvas()
        from kivy.graphics.vertex_instructions import Rectangle, Ellipse

        self.bars = []

        with self.canvas.before:
            for value in self.values:
                self.bars.append(
                    (
                        Ellipse(angle_start=-90, angle_end=90, segments=10, size=(1, 1)),
                        Rectangle(size=(1, 1)))
                )

    def update_elements(self, *args, **kwargs):
        super(BarDiagramElementsContainer, self).update_elements(*args, **kwargs)
        if not self.values:
            Logger.info("Diagram: values are empty, won't locate bars")
            return

        width = self.width / len(self.values)
        max_y = float(max(self.values))

        if max_y < 0.01:
            return

        for i, (ellipse, rect) in enumerate(self.bars):

            if self.values[i] < 0.001:
                rect.size = (0, 0)
                ellipse.size = (0, 0)
                continue

            diameter = width - self.spacing / 2. if self.values[i] > 0.001 else 0
            ellipse.size = (diameter, diameter)
            x = self.x + width * i
            y = self.y

            rect.pos = (x, y)

            height = self.height * (self.values[i] / max_y)
            if height < 0:
                height = 0

            rect.size = (diameter, height - diameter / 2.)

            ellipse.pos = (x, y + height - diameter)
            i += 1

    def __init__(self, **kwargs):
        super(BarDiagramElementsContainer, self).__init__(**kwargs)
        self.bars = None


class StatsDiagram(object):
    family = StringProperty('', allownone=True)
    POINT_VALUES = None

    def interpolated_values(self):
        from utils import Interpolator
        percents = self.get_percentages()
        points = sorted(self.values.keys())

        # if all the values are there, there is no need to interpolate anything
        if all(point in percents for point in self.values):
            return percents

        # can't interpolate such a small set of values
        if len(percents) == 1:
            return {point: percents.values()[0] for point in points}

        float_keys = [float(key) for key in percents.keys() if points[0] <= key <= points[-1]]
        float_keys.sort()

        if not float_keys:
            return {}

        float_values = [percents[int(float_key)] for float_key in float_keys]
        # add fake values at begin and end make a loop interpolation
        loop_length = len(self.values)
        ex_float_keys = list(float_keys)
        ex_float_values = list(float_values)
        if int(float_keys[0]) != points[0]:
            if not float_keys[-1] - loop_length in float_keys:
                ex_float_keys = [float_keys[-1] - loop_length] + float_keys
                ex_float_values = [float_values[-1]] + float_values
        if int(float_keys[-1]) != points[-1]:
            if not float_keys[0] + loop_length in float_keys:
                ex_float_keys.append(float_keys[0] + loop_length)
                ex_float_values.append(float_values[0])
        try:
            interpolator = Interpolator(ex_float_keys, ex_float_values)
        except ValueError, ex:
            Logger.error("Error while interpolation. Values: %s, %s" % (ex_float_keys, ex_float_values))
            raise ex

        result = {value: interpolator[float(value)] if value not in percents.keys() else percents[value] for value in
                  points}

        return result

    def on_family(self, *args, **kwargs):
        from settings import ACTIVITY_COLORS_TRANSPARENT

        self.color = ACTIVITY_COLORS_TRANSPARENT[self.family]
        self.update()

    def get_percentages(self):  # pragma: no cover
        raise NotImplementedError()

    def update(self):
        Logger.info("Diagram: Update, %s, %s" % (self.__class__, self.family))
        percents = self.interpolated_values()
        if percents:
            Logger.info("Diagram: Percents okay - %s entries" % len(percents.keys()))
            if not all([value == 0 for value in self.values.values()]):
                animation = Animation(values=percents, duration=.5, t='in_out_quint')
                animation.start(self)
            else:
                self.values = percents
        else:
            from library_widgets import OkCancelPopup

            if popup_open(OkCancelPopup):
                return

            manager = App.get_running_app().manager

            if manager.current == 'tasks':
                return

            popup = OkCancelPopup(
                text=_("This is your first test in this category, so there is no statistics. "
                       "Please finish the test to get some.")
            )

            def to_activities():
                manager.to_screen('activity')
                popup.dismiss()

            def to_tasks():
                if manager.current == 'tasks':
                    popup.dismiss()
                    return

                popup.dismiss()
                App.get_running_app().manager.state = 'closed'
                tasks_screen = manager.get_screen('tasks')
                tasks_screen.family = self.family
                tasks_screen.quick_test = True
                tasks_screen.main_manager.current = 'test'
                manager.to_screen('tasks')

            popup.cancel_callback = to_activities
            popup.ok_callback = to_tasks
            popup.open()


class FilledLineDiagram(Diagram):
    pass


class BarStatsDiagram(StatsDiagram, Diagram):
    def __init__(self, **kwargs):
        super(BarStatsDiagram, self).__init__(**kwargs)
        if self.POINT_VALUES:
            self.values = zip(self.POINT_VALUES, [0] * len(self.POINT_VALUES))


class FilledLineStatsDiagram(StatsDiagram, FilledLineDiagram):
    def __init__(self, **kwargs):
        super(FilledLineStatsDiagram, self).__init__(**kwargs)
        if self.POINT_VALUES:
            self.values = zip(self.POINT_VALUES, [0] * len(self.POINT_VALUES))
