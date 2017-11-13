from kivy.logger import Logger
from kivy.app import App
from kivy.utils import platform
import settings


class KognitivoApp(App):
    use_kivy_settings = False

    user_data_dir = settings.DATABASE_PATH

    def open_settings(self, *largs):
        if not self.settings_cls:
            from settings_widget import KognitivoSettings

            self.settings_cls = KognitivoSettings
        super(KognitivoApp, self).open_settings(*largs)

    def on_stop(self):
        if platform == 'linux':
            self.profile.disable()
            self.profile.dump_stats('kognitivo.profile')
        self.profiler.print_all()
        if self.billing:
            self.billing.unbind()

    @property
    def tracker(self):
        if not self._tracker:
            Logger.info("Tracker: initialization")
            from tracking import Tracker

            self._tracker = Tracker()
        return self._tracker

    def _initialize_storage(self):
        Logger.info("Storage: initialization")

        from kivy.storage.jsonstore import JsonStore

        self._storage = JsonStore("storage-%s.json" % self.name)
        import settings

        for key, config in settings.DEFAULT_STORAGE_CONFIG.items():
            if key not in self._storage:
                self._storage.put(key, **config)

        records = self._storage["task_records"]
        for key in settings.TASKS:
            if key not in records:
                records[key] = 0
        self._storage.put("task_records", **records)

        starts_count = self._storage['starts']['count']

        self.tracker.send_event('general', 'start', value=starts_count + 1)
        self._storage['starts'] = {"count": starts_count + 1}
        Logger.info("Storage: started %s times" % self._storage['starts']['count'])

    @property
    def storage(self):
        if not self._storage:
            self._initialize_storage()
        return self._storage

    def _initialize_gplay_services(self):
        from gplay import GoogleClient
        import settings
        self._google_client = GoogleClient()

        if not settings.PROFILE:
            auto_login = self.config.get('preferences', 'google_auto_login')
            if auto_login == "1":
                self._google_client.connect()

    @property
    def google_client(self):
        if not self._google_client:
            Logger.info("Google: initialization")
            self._initialize_gplay_services()
        return self._google_client

    def initialize_cprofile(self):
        if platform == 'linux':
            import cProfile

            self.profile = cProfile.Profile()
            self.profile.enable()

    def __init__(self, name=None, **kwargs):
        from utils import NaiveProfiler

        self.profiler = NaiveProfiler()
        self.initialize_cprofile()
        self.profiler.fix_from("---app-init")

        # lazy attributes
        self._tracker = None
        self._sounds = None
        self.billing = None
        self._storage = None
        self.lang = None
        self.manager = None
        self._google_client = None
        self.profiler.fix_from("super init")
        super(KognitivoApp, self).__init__(**kwargs)
        self.profiler.fix_to("super init")

        self.db_path = None
        self.profiler.fix_from("import-configure")
        from configure import configure

        self.profiler.fix_to("import-configure")

        self.profiler.fix_from("configure")
        configure()
        self.profiler.fix_to("configure")

        from settings import DEVELOPMENT_VERSION

        if name is None:
            KognitivoApp.name = "kognitivo-dev" if DEVELOPMENT_VERSION else "kognitivo"
        else:
            KognitivoApp.name = name
        self.service = None

        self.profiler.fix_to("---app-init")

    def build_service_params(self):
        params = {
            "enable_notifications": self.config.get('preferences', 'enable_notifications'),
            "morning_notification_time": self.config.get('preferences', 'morning_notification_time'),
            "lunch_notification_time": self.config.get('preferences', 'lunch_notification_time'),
            "evening_notification_time": self.config.get('preferences', 'evening_notification_time'),
            "language": self.config.get('preferences', 'language'),
        }
        return params

    def schedule_notifications(self, force=False):
        if platform == 'android':
            from notifications_scheduler import Scheduler

            scheduler = Scheduler([self.config.get('preferences', 'morning_notification_time'),
                                   self.config.get('preferences', 'lunch_notification_time'),
                                   self.config.get('preferences', 'evening_notification_time')])
            enable_notifications = int(self.config.get('preferences', 'enable_notifications'))
            if enable_notifications == 1:
                Logger.debug("Notifications: Creating schedules...")
                if force:
                    scheduler.clean_schedules()
                scheduler.create_schedule()
                Logger.debug("Notifications: Finished creating schedules")
            elif enable_notifications == 0:
                if force:
                    scheduler.clean_schedules()
            return
        else:
            Logger.info("Notifications: no notifications on %s" % platform)

    def set_language(self):
        if platform == 'android':
            if self.config.get('preferences', 'language') == 'system':
                Logger.info("Locale: Setting locale to system preference...")
                from jnius import autoclass

                Locale = autoclass('java.util.Locale')

                try:
                    system_language = Locale.getDefault().getLanguage()
                except Exception:
                    system_language = 'en'

                Logger.info("Locale: System locale is %s" % system_language)
                from settings import LANGUAGES

                if system_language in LANGUAGES:
                    self.lang = system_language
                    self.config.set('preferences', 'language', system_language)
                else:
                    Logger.info("Locale: System locale is unknown. Falling back to english...")
                    self.lang = 'en'
                    self.config.set('preferences', 'language', 'en')
                self.config.write()
        self.lang = self.config.get('preferences', 'language')
        from utils import _

        _.switch_lang(self.lang)

    def _initialize_sounds(self):
        Logger.info('App: initialize sounds')
        if settings.SOUND_ENABLED and int(self.config.get('preferences', 'sound')) == 1:
            self._sounds = {}
            from settings import SOUNDS
            from kivy.core.audio import SoundLoader

            for name, path in SOUNDS.items():
                self._sounds[name] = SoundLoader.load(path)
        else:
            from collections import defaultdict
            from kivy.core.audio import Sound

            self._sounds = defaultdict(Sound)

    def initialize_billing(self, callback=None, *args):
        if not self.billing:
            Logger.info("Billing: initialization")
            self.profiler.fix_from('billing')
            from billing import BillingService

            self.billing = BillingService()
            self.billing.bind(callback)
            self.profiler.fix_to('billing')
        else:
            if callback:
                callback()

    @property
    def sounds(self):
        if not self._sounds:
            self._initialize_sounds()
        return self._sounds

    def build(self):
        self.profiler.fix_from('---build')
        self.profiler.fix_from('set_language')
        self.set_language()
        self.profiler.fix_to('set_language')

        self.profiler.fix_from('schedule_notifications')
        self.schedule_notifications()
        self.profiler.fix_to('schedule_notifications')

        self.profiler.fix_from('import-root-widget')
        from root_manager import RootManager

        self.profiler.fix_to('import-root-widget')

        self.profiler.fix_from('build-root-widget')
        import settings

        root = RootManager()
        from managers.database import database_manager
        if database_manager.total_count() > 1:
            from screens.activity.activity import ActivityScreen
            start_screen = ActivityScreen()
            menu_state = 'open'
        else:
            from screens.tutorial import TutorialScreen
            start_screen = TutorialScreen()
            menu_state = 'closed'

        root.add_widget(start_screen)
        from screens.menu import KognitivoNavigator
        navigator = KognitivoNavigator()
        navigator.add_widget(root)
        navigator.state = menu_state

        from kivy.core.window import Window
        Window.clearcolor = (1, 1, 1, 1)
        if settings.DEVELOPMENT_VERSION and settings.INSPECT and platform == 'linux':
            from kivy.modules import inspector
            inspector.create_inspector(Window, root)
        self.profiler.fix_to('build-root-widget')
        self.manager = root

        self.bind(on_start=self.post_build_init)

        self.profiler.fix_to('---build')
        return navigator

    def post_build_init(self, *_):
        self.profiler.fix_from('post-build')
        from managers.facebook import facebook_manager
        facebook_manager.initialize()
        from kivy.core.window import Window

        win = Window
        win.bind(on_keyboard=self.key_handler)
        self.root.attach_toggle(win)
        self.profiler.fix_to('post-build')

    # noinspection PyUnusedLocal
    def key_handler(self, window, keycode1, *_):
        if keycode1 in [27, 1001]:
            if not self.close_settings():
                self.manager.go_back()
            return True
        return False

    def build_settings(self, settings):
        with open("settings.json", "r") as settings_json:
            from utils import _

            settings.add_json_panel(_('SETTINGS'), self.config, data=settings_json.read())

    def build_config(self, config):
        from settings import KIVY_DEFAULT_CONFIG

        for section, conf in KIVY_DEFAULT_CONFIG.items():
            config.setdefaults(section, conf)

    def on_pause(self):
        from managers.facebook import facebook_manager
        facebook_manager.activate()
        return True

    def on_resume(self):
        from managers.facebook import facebook_manager
        facebook_manager.deactivate()

    def on_config_change(self, config, section, key, value):
        self.schedule_notifications(force=True)
        if section == 'preferences':
            if key == 'language':
                Logger.info("Settings: change locale to %s" % value)
                self.lang = value

            if key == 'sound':
                self._initialize_sounds()

            if key == 'enable_notifications':
                self.tracker.send_event('general', 'notifications', 'disabled' if value == "0" else 'enabled')
