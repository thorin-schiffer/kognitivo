from kivy import Logger, platform
from kivy.app import App


class AbstractVibrationManager(object):
    def turned_on(self):
        config = App.get_running_app().config
        if int(config.get('preferences', 'vibration')) == 1:
            return True
        else:
            return False

    def vibrate(self, length):
        if not self.turned_on():
            Logger.error("Android Vibration: won't vibrate, turned off in settings...")
            return

        Logger.info("Vibrator: vibrate %s milliseconds...", length)


class DummyVibrationManager(AbstractVibrationManager):
    pass


if platform == 'android':
    from jnius import autoclass

    python_activity = autoclass('org.kivy.android.PythonActivity').mActivity
    Context = autoclass('android.content.Context')

    class AndroidVibrationManager(AbstractVibrationManager):
        def __init__(self):
            self.service = None

        def initialize(self):
            self.service = python_activity.getSystemService(Context.VIBRATOR_SERVICE)

        def vibrate(self, length):
            if not self.turned_on():
                Logger.error("Android Vibration: won't vibrate, turned off in settings...")
                return
            super(AndroidVibrationManager, self).vibrate(length)

            if not self.service:
                self.initialize()
                if not self.service:
                    Logger.error("Android Vibration: failed to initialize vibration service")
                    return
            self.service.vibrate(int(length))

    vibration_manager = AndroidVibrationManager()
else:
    vibration_manager = DummyVibrationManager()
