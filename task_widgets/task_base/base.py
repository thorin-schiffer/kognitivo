from datetime import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout

from kivy.properties import BooleanProperty, NumericProperty
from kivy.properties import ObjectProperty

# do not delete!
# noinspection PyUnresolvedReferences
from task_widgets.task_base import status_bar as task_status_bar  # noqa F401
from utils import import_kv
from .intro_hint import IntroHint
from .mixins import DescriptionAnswerMixin

import_kv(__file__)


def inverse_time_efficiency(seconds):
    """
    Efficiency strategy for time connected tasks.
    @param seconds: task duration in seconds
    @return: Efficiency in interval (0, 1)
    """
    return 1. / (seconds + 1)


class BaseTask(AnchorLayout, DescriptionAnswerMixin):
    # properties to overload
    SIZE = None
    TASK_KEY = None
    MISTAKE_FINE = 5
    MAX_DURATION = 60
    INTRO_HINT_CLASS = IntroHint
    successful = BooleanProperty(False)
    mistakes_count = NumericProperty(0)
    num_succeed = NumericProperty(0)
    seconds_to_success = NumericProperty(0.0)
    status_bar = ObjectProperty()
    main_area = ObjectProperty()
    EFFICIENCY_TO_POINTS = 10000

    def on_mistakes_count(self, *args, **kwargs):
        self.status_bar.mistakes_count = self.mistakes_count

    def __init__(self, **kwargs):
        self.correct_answer = None
        self.start_time = None
        self.points = None
        self.efficiency = 0
        import settings
        self.intro_hint = self.INTRO_HINT_CLASS(task=self)
        self.families = settings.TASKS[self.TASK_KEY]['families']
        super(BaseTask, self).__init__(**kwargs)

    def add_main_widgets(self):
        self.main_area.add_widget(self.get_description_widget())
        self.main_area.add_widget(self.get_answer_widget())

    def show_intro_hint(self):
        if App.get_running_app().manager.current != 'tasks':
            return
        if self.intro_hint.parent is None and not self.seconds_to_success:
            self.main_area.add_widget(self.intro_hint)
            self.intro_hint.tutorial.start()

    def on_seconds_to_success(self, *args, **kwargs):
        self.status_bar.time = self.seconds_to_success

    def on_num_succeed(self, *args, **kwargs):
        self.status_bar.correct_count = self.num_succeed

    def _calculate_seconds_to_success(self, *_):
        if not self.start_time:
            return
        self.seconds_to_success = (datetime.now() - self.start_time).total_seconds()
        self._fine_for_mistakes()
        if self.seconds_to_success > self.MAX_DURATION:
            self.finish(False)

    def _fine_for_mistakes(self):
        self.seconds_to_success += self.mistakes_count * self.MISTAKE_FINE

    def mark_successful(self, *args, **kwargs):
        self.successful = True

    def final_animation(self, *args, **kwargs):
        for i, child in enumerate(self.main_area.children):
            if i == len(self.main_area.children) - 1:
                self.hide_animation.bind(on_complete=self.mark_successful)
            self.hide_animation.start(child)

    def _process_achievements(self):
        app = App.get_running_app()
        app.google_client.increment_achievement("sergeant_cognitive")
        app.google_client.increment_achievement("major_cognitive")
        app.google_client.increment_achievement("lieutenant_cognitive")
        app.google_client.increment_achievement("colonel_cognitive")
        app.google_client.increment_achievement("general_cognitive")

    def finish(self, update_status=True):
        if self.successful:
            return
        self.efficiency = inverse_time_efficiency(self.seconds_to_success)
        self.points = int(self.efficiency * self.EFFICIENCY_TO_POINTS)

        if update_status:
            self._calculate_seconds_to_success()

        self.status_bar.points = self.points
        Clock.unschedule(self._calculate_seconds_to_success)
        self.final_animation()

        from managers.database import database_manager
        database_manager.add_stat(key=self.TASK_KEY,
                                  efficiency=self.efficiency,
                                  duration=self.seconds_to_success)
        self._process_achievements()
        App.get_running_app().tracker.send_event('tasks', 'class', label=self.TASK_KEY)

    def break_task(self):
        self.intro_hint.tutorial.stop()
        self.main_area.remove_widget(self.intro_hint)
        self.points = 0
        Clock.unschedule(self._calculate_seconds_to_success)

    def on_incorrect_answer(self, button):
        from managers.vibration import vibration_manager
        App.get_running_app().sounds['fail'].play()
        vibration_manager.vibrate(100)
        button.mark_incorrect()
        button.unbind(on_press=self._check_answer)
        self.mistakes_count += 1

    def on_correct_answer(self, button):
        App.get_running_app().sounds['success'].play()
        button.mark_correct()
        self.num_succeed += 1
        self.finish()

    def _check_answer(self, widget):
        if self.correct_answer is None:
            raise ValueError("Task.correct_answer should be set")

        if not self.successful:
            value = widget.value

            if value == self.correct_answer:
                self.on_correct_answer(widget)
            else:
                self.on_incorrect_answer(widget)

    def on_parent(self, _, value):
        if value:
            self.show_intro_hint()
