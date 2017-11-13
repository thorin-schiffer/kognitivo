from kivy import Logger

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget

from datetime import datetime
from answer_widgets import BaseAnswerWidget
from description_widgets import BaseDescriptionWidget
from utils import import_kv

import_kv(__file__)


class DescriptionAnswerMixin(Widget):
    DESCRIPTION_WIDGET_CLASS = BaseDescriptionWidget
    ANSWER_WIDGET_CLASS = BaseAnswerWidget

    description_widget = ObjectProperty()
    answer_widget = ObjectProperty()

    def get_description_widget(self, **kwargs):
        self.description_widget = self.DESCRIPTION_WIDGET_CLASS(**kwargs)
        return self.description_widget

    def get_answer_widget(self, **kwargs):
        self.answer_widget = self.ANSWER_WIDGET_CLASS(**kwargs)
        return self.answer_widget

    def get_correct_answer_widgets(self, **kwargs):
        widgets = self.answer_widget.get_values_widgets()[self.correct_answer]
        return [widget for widget in widgets if widget.correctness_state is not True]

    def get_incorrect_answer_widgets(self, **kwargs):
        correct_widgets = self.get_correct_answer_widgets()
        result = []
        for widgets in self.answer_widget.get_values_widgets().values():
            for widget in widgets:
                if widget not in correct_widgets:
                    result.append(widget)
        return result


class ValueMixin(object):
    value = ObjectProperty()


class RemainBarWidget(Widget):
    pass


class StartMixin(DescriptionAnswerMixin):
    def start(self, *args, **kwargs):
        App.get_running_app().sounds['start'].play()
        self.intro_hint.tutorial.stop()
        self.main_area.remove_widget(self.intro_hint)
        self.intro_hint = None
        self.add_main_widgets()
        Clock.schedule_interval(self._calculate_seconds_to_success, 1. / 2)
        Logger.info("Start class %s started..." % self.__class__)


class StartOnTimeoutMixin(StartMixin):
    remain_bar = ObjectProperty()
    REMAIN_BAR_WIDGET_CLASS = RemainBarWidget
    SHOW_TIME = None

    # what happens on timeout. This method is to overload
    def on_timeout(self, *args, **kwargs):
        self.description_widget.remove_widget(self.remain_bar)
        self.start_time = datetime.now()
        self.status_bar.show()

    def append_remain_bar(self, **kwargs):
        self.remain_bar = self.REMAIN_BAR_WIDGET_CLASS()
        self.description_widget.add_widget(self.remain_bar)

    def on_intro_hint_hide(self):
        pass

    def start(self, *args, **kwargs):
        def on_complete(*args):
            super(StartOnTimeoutMixin, self).start(*args, **kwargs)
            self.on_intro_hint_hide()
            if self.SHOW_TIME is None:
                raise NotImplementedError("Set show_time attribute in the child of StartOnTimeoutMixin")
            self.append_remain_bar()
            Clock.schedule_once(self.on_timeout, timeout=self.SHOW_TIME)
            Animation(size_hint_x=0, opacity=0, duration=self.SHOW_TIME, t='in_out_cubic').start(self.remain_bar)

        animation = Animation(opacity=0, duration=.5, t="in_out_cubic")
        animation.bind(on_complete=on_complete)
        animation.start(self.intro_hint)


class StartImmediatelyMixin(StartMixin):
    def on_intro_hint_hide(self):
        pass

    def start(self, *args, **kwargs):
        def on_complete(*args):
            self.on_intro_hint_hide()
            super(StartImmediatelyMixin, self).start(*args, **kwargs)
            self.start_time = datetime.now()
            self.status_bar.show()

        animation = Animation(opacity=0, duration=.5, t="in_out_cubic")
        animation.bind(on_complete=on_complete)
        animation.start(self.intro_hint)

