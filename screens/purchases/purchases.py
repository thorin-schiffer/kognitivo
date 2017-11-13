from kivy import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

from kivy.properties import ObjectProperty, partial

from library_widgets import TrackingScreenMixin
from utils import import_kv

import_kv(__file__)


class PurchaseScreen(TrackingScreenMixin, Screen):
    loading = ObjectProperty()

    def __init__(self, **kw):
        self._container = None
        super(PurchaseScreen, self).__init__(**kw)

    @property
    def container(self):
        if not self._container:
            Logger.info("Purchases: container initialization")
            from .content import PurchasesContainer
            self._container = PurchasesContainer()
        return self._container

    def add_content(self, *args, **kwargs):
        if self.container.parent != self:
            App.get_running_app().tracker.send_event('clicks', 'menu', 'purchase')
            Logger.info("Purchases: container initialization finished")
            self.loading.hide(self._container)
        else:
            self.container.start()

    def on_enter(self):
        app = App.get_running_app()
        app.tracker.send_event('purchase', 'screen', 'enter')
        billing_trigger = Clock.create_trigger(partial(app.initialize_billing, self.add_content))
        billing_trigger()

    def on_leave(self, *args):
        self.container.stop()
