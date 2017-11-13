from tracking.abstract import AbstractTracker
from jnius import autoclass, JavaException

ScreenViewBuilder = autoclass('com.google.android.gms.analytics.HitBuilders$ScreenViewBuilder')
EventBuilder = autoclass('com.google.android.gms.analytics.HitBuilders$EventBuilder')
GoogleAnalytics = autoclass('com.google.android.gms.analytics.GoogleAnalytics')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
AndroidString = autoclass('java.lang.String')


class GoogleTracker(AbstractTracker):
    def __init__(self):
        self.tracker = None

    def _get_tracker(self):
        if self.tracker:
            return self.tracker
        import settings

        try:
            app = PythonActivity.getApplication()

            analytics = GoogleAnalytics.getInstance(app)
            if settings.DEVELOPMENT_VERSION:
                analytics.setDryRun(True)

            tracker = analytics.newTracker(AndroidString(settings.GOOGLE_ANALYTICS_TRACKING_ID))
            tracker.setSessionTimeout(300)
            tracker.enableAdvertisingIdCollection(True)
        except JavaException:
            return None
        self.tracker = tracker
        return tracker

    def send_screen(self, screen):
        super(GoogleTracker, self).send_screen(screen)
        tracker = self._get_tracker()
        if not tracker:
            return

        tracker.setScreenName(AndroidString(screen.name))
        tracker.send(ScreenViewBuilder().build())

    def clear_screen(self):
        super(GoogleTracker, self).clear_screen()
        tracker = self._get_tracker()
        if not tracker:
            return

        tracker.setScreenName(None)

    def send_event(self, category, action, label=None, value=None):
        super(GoogleTracker, self).send_event(category, action, label)
        tracker = self._get_tracker()
        if not tracker:
            return

        event = EventBuilder().setCategory(category).setAction(action)
        if label:
            event.setLabel(label)

        if value:
            event.setValue(int(value))

        tracker.send(event.build())

    def send_to_server(self):
        super(GoogleTracker, self).send_to_server()
        GoogleAnalytics.getInstance(PythonActivity.getBaseContext()).dispatchLocalHits()
