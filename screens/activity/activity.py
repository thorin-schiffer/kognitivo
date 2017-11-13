# -*- coding: utf-8 -*-
from kivy import Logger

from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen

from library_widgets import TrackingScreenMixin
from utils import import_kv

import_kv(__file__)


class ActivityScreen(TrackingScreenMixin, Screen):
    _panel = ObjectProperty()
    family = StringProperty('', allownone=True)
    loading = ObjectProperty()

    def __init__(self):
        super(ActivityScreen, self).__init__()
        self._tutorial_shown = False

    @property
    def panel(self):
        if not self._panel:
            Logger.info("Activity: panel initialization")
            from .content import StatsPanel

            self._panel = StatsPanel()
            app = App.get_running_app()
            # noinspection PyStatementEffect
            app.storage
            # noinspection PyStatementEffect
            app.tracker
            # noinspection PyStatementEffect
            app.google_client
        return self._panel

    def on_pre_leave(self, *args):
        app = App.get_running_app()
        if app.storage['starts']['count'] > 3:
            app.google_client.unlock_achievement("faithful_comrade")

    def _to_show_rate_popup(self):
        app = App.get_running_app()
        storage = app.storage
        to_show_rate = storage['feedback']['status'] is None and storage['starts']['count'] > 1
        to_show_rate |= not storage['feedback']['status'] and storage['starts']['count'] % 10 == 0
        return to_show_rate

    def _to_show_like_popup(self):
        app = App.get_running_app()
        storage = app.storage
        to_show_like = storage['facebook_like']['status'] is None and storage['starts']['count'] > 5
        to_show_like |= not storage['feedback']['status'] and storage['starts']['count'] % 20 == 0
        return to_show_like

    def show_popups(self):

        app = App.get_running_app()

        if app.manager.has_screen('tutorial'):
            return

        if self._to_show_rate_popup():
            app.tracker.send_event('clicks', 'rate_popup', 'showed')
            from content import RatePopup

            RatePopup().open()
        else:
            if self._to_show_like_popup():
                app.tracker.send_event('clicks', 'fb_like_popup', 'showed')
                from content import LikePopup

                LikePopup().open()

    def update_content(self, *args):
        if self.panel.parent != self:
            Logger.info("Activity: panel initialization finished")
            self.family = None
            self.loading.hide(self.panel)
        else:
            self.show_popups()
        self.panel.update()
        from kivy.clock import Clock

        Clock.schedule_once(self.check_tutorial, timeout=1.5)

    def on_enter(self, *args, **kwargs):
        super(ActivityScreen, self).on_enter(*args, **kwargs)
        app = App.get_running_app()
        app.initialize_billing(self.update_content)

    def _tutorial_finished(self, *args):
        from library_widgets import OkPopup
        from utils import _
        finished_popup = OkPopup(text=_("Congratulations! This tutorial is finished. Happy researching!"))
        App.get_running_app().sounds['test_finished'].play()
        finished_popup.bind(on_dismiss=lambda *args: App.get_running_app().root.toggle_state())
        finished_popup.open()

    def check_tutorial(self, *args, **kwargs):
        from managers.database import database_manager

        app = App.get_running_app()
        if (database_manager.total_count() == 1 or app.manager.has_screen(
                'tutorial')) and not self._tutorial_shown:
            self._tutorial_shown = True
            self.panel.day_tab.diagram.on_tutorial_start = lambda: self.panel.tab_panel.switch_to(self.panel.day_tab)
            self.panel.week_tab.diagram.on_tutorial_start = lambda: self.panel.tab_panel.switch_to(self.panel.week_tab)
            self.panel.progress_tab.diagram.on_tutorial_start = lambda: self.panel.tab_panel.switch_to(
                self.panel.progress_tab)
            self.panel.calendar_tab.diagram.on_tutorial_start = lambda: self.panel.tab_panel.switch_to(
                self.panel.calendar_tab)
            self.panel.filter_panel.on_tutorial_start = lambda: self.panel.filter_panel.toggle()
            self.panel.filter_panel.on_tutorial_finish = lambda: self.panel.filter_panel.toggle()
            self.panel.filter_panel.bind(on_tutorial_finish=self._tutorial_finished)
            self.panel.now_tab.diagram.show_tutorial(next_widgets=[
                self.panel.day_tab.diagram,
                self.panel.week_tab.diagram,
                self.panel.progress_tab.diagram,
                self.panel.calendar_tab.diagram,
                self.panel.filter_panel,
            ])

    def on_family(self, *args, **kwargs):
        self.panel.family = self.family
