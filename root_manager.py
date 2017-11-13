from kivy import Logger
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager


class RootManager(ScreenManager):
    stats_label = ObjectProperty()

    def get_screen(self, name):
        if not self.has_screen(name):
            self._build_screen(name)
        return super(RootManager, self).get_screen(name)

    def _build_screen(self, name):
        Logger.info("Root widget: building %s screen" % name)
        if name == 'activity':
            from screens.activity import activity

            screen = activity.ActivityScreen()
            self.add_widget(screen)
            return

        if name == 'tasks':
            from screens.tasks import tasks

            screen = tasks.TasksScreen()
            self.add_widget(screen)
            return

        if name == 'purchases':
            from screens.purchases import purchases

            screen = purchases.PurchaseScreen()
            self.add_widget(screen)
            return

        if name == 'tutorial':
            from screens.tutorial import TutorialScreen

            screen = TutorialScreen()
            self.add_widget(screen)
            return

        raise RuntimeError("Unknown screen")

    def to_screen(self, name):
        # pure performance tweak to postpone screens instantiation
        if not self.has_screen(name):
            self._build_screen(name)
        from kivy.uix.widget import WidgetException
        Logger.info("Root Widget: switch to screen %s" % name)
        try:
            self.current = name
        except WidgetException as ex:
            Logger.error("Root Widget: can't switch %s, because %s" % (name, unicode(ex)))

    def go_back(self):
        from kivy.app import App
        from kivy.uix.widget import WidgetException

        if self.screen_names.index(self.current) == 0:
            app = App.get_running_app()
            app.stop()
        else:
            try:
                self.current = self.previous()
            except WidgetException:
                pass

    def __init__(self, *args, **kwargs):
        import settings

        if settings.DEVELOPMENT_VERSION and settings.SHOW_STATS:
            from kivy.uix.label import Label
            from kivy.metrics import dp
            from kivy.clock import Clock

            import os

            self._proc_status = '/proc/%d/status' % os.getpid()

            self._scale = {'kB': 1024.0, 'mB': 1024.0 * 1024.0,
                           'KB': 1024.0, 'MB': 1024.0 * 1024.0}

            self.stats_label = Label(
                text="PENDING...",
                text_size=(dp(400), dp(300)),
                halign='left',
                valign='middle'
            )
            Clock.schedule_interval(self.update_stats, timeout=1)
            self.stats_label.texture_update()

        super(RootManager, self).__init__(*args, **kwargs)

    def update_stats(self, *arg, **kwargs):
        import sys
        import os
        from kivy.clock import Clock

        project_path = os.path.dirname(__file__)
        kivy_modules = [name for name in sys.modules.keys() if name.startswith("kivy.")]
        project_modules = [name for name, module in sys.modules.items() if
                           module and getattr(module, '__file__', "").startswith(
                               project_path) and name not in kivy_modules]
        message = ""
        message += "Modules imported: %s\n" % (len(sys.modules))
        message += "Kivy modules imported: %s\n" % (len(kivy_modules))
        message += "Project modules imported: %s\n" % (len(project_modules))
        message += "Widgets attached: %s\n" % len(list(self.walk()))

        memory = self._get_memory() / (1024 * 1024)
        message += "Memory usage: %.1f MB\n" % memory

        from kivy.lang import Builder

        message += "KV files count: %s\n" % len(Builder.files)

        message += "FPS: %s\n" % int(Clock.get_fps())
        self.stats_label.text = message

    def _VmB(self, VmKey):
        try:
            t = open(self._proc_status)
            v = t.read()
            t.close()
        except Exception:
            return 0.0  # non-Linux?
            # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
        i = v.index(VmKey)
        v = v[i:].split(None, 3)  # whitespace
        if len(v) < 3:
            return 0.0  # invalid format?
        # convert Vm value to bytes
        return float(v[1]) * self._scale[v[2]]

    def _get_memory(self, since=0.0):
        return self._VmB('VmRSS:') - since
