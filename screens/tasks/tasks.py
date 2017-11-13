from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.app import App
from kivy.logger import Logger

from library_widgets import TrackingScreenMixin

from utils import import_kv

import_kv(__file__)


class TasksScreen(TrackingScreenMixin, Screen):
    family = StringProperty(None, allownone=True)
    played_times = NumericProperty()
    tasks = ListProperty()
    _main_manager = ObjectProperty()
    loading = ObjectProperty()
    quick_test = BooleanProperty(False)

    def on_quick_test(self, *args):
        if self._main_manager:
            self.update_content()

    @property
    def main_manager(self):
        if not self._main_manager:
            from .content import TaskScreenManager

            self._main_manager = TaskScreenManager()
        return self._main_manager

    def update_content(self, *args, **kwargs):
        if self.quick_test:
            self.main_manager.start_test(self.family, self.tasks)
            self.main_manager.current = 'test'
        else:
            self.main_manager.task_sets_screen.fill()
            self.main_manager.current = 'task_sets'
        app = App.get_running_app()
        sessions_starts = app.storage['sessions']['started']

        app.tracker.send_event('tasks', 'sessions', label='started', value=sessions_starts + 1)
        app.storage['sessions'] = {"started": sessions_starts + 1,
                                   "finished": app.storage['sessions']['finished']}
        self.played_times += 1
        Logger.info("Tasks: playing %s times" % self.played_times)
        if self.played_times == 10:
            App.get_running_app().google_client.unlock_achievement("addicted")
        if self.main_manager.parent != self:
            self.loading.hide(self._main_manager)

    def on_enter(self, *args):
        super(TasksScreen, self).on_enter(*args)
        app = App.get_running_app()
        app.initialize_billing(self.update_content)
