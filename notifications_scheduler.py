from datetime import datetime, timedelta
from jnius import autoclass
from kivy.logger import Logger
# noinspection PyUnresolvedReferences

Context = autoclass('android.content.Context')
Intent = autoclass('android.content.Intent')
PendingIntent = autoclass('android.app.PendingIntent')
Receiver = autoclass('org.kognitivo.kognitivo.Receiver')
AndroidString = autoclass('java.lang.String')

receiver_class = Receiver().getClass()

activity = autoclass('org.kivy.android.PythonActivity').mActivity

def android_schedule_time(elapsed_time, schedule_datetime):
    """
    Returns the value got through SystemClock.elapsedRealtime to python datetime object.
    :param elapsed_time: time by elapsedRealtime (millise since boot)
    :return: datetime object of a boot time
    """
    boot_time = datetime.now() - timedelta(milliseconds=elapsed_time)
    return (schedule_datetime - boot_time).total_seconds() * 1000


class Scheduler(object):
    PENDING_INTENT_REQUEST_CODE = 889754

    def __init__(self, schedule_times):
        self.schedule_times = [datetime.strptime(schedule, '%H:%M').time() for schedule in schedule_times]
        self.alarm_manager = None
        self.pending_intent = None

    def get_intent(self):
        from utils import _

        intent = Intent(activity, receiver_class)
        intent.setAction(Intent.ACTION_PROVIDER_CHANGED)
        intent.putExtra("message", AndroidString(_("It's time to measure your skills!")))
        return intent

    def schedule_datetimes(self):
        today = datetime.now().date()
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        candidates = [datetime.combine(today, schedule_time) for schedule_time in self.schedule_times]
        candidates += [datetime.combine(tomorrow, schedule_time) for schedule_time in self.schedule_times]
        candidates = [candidate for candidate in candidates if candidate > datetime.now()]
        candidates.sort()
        return candidates[:3]

    def get_schedules(self):
        intent = self.get_intent()
        pending_intents = []
        for i in range(len(self.schedule_times)):
            pending_intent = PendingIntent.getBroadcast(activity, self.PENDING_INTENT_REQUEST_CODE + i, intent, PendingIntent.FLAG_NO_CREATE)
            pending_intents.append(pending_intent)
        return pending_intents

    def clean_schedules(self):
        am = activity.getSystemService(Context.ALARM_SERVICE)
        for pi in self.get_schedules():
            if pi:
                Logger.info("Notifications: revoke schedule %s" % pi)
                am.cancel(self.pending_intent)
                pi.cancel()

    def create_schedule(self):
        already_scheduled = self.get_schedules()
        if all(schedule for schedule in already_scheduled):
            Logger.info("Notifications: already scheduled, pass...")
            return
        SystemClock = autoclass('android.os.SystemClock')
        AlarmManager = autoclass('android.app.AlarmManager')

        self.alarm_manager = activity.getSystemService(Context.ALARM_SERVICE)
        schedule_datetimes = self.schedule_datetimes()
        intent = self.get_intent()
        for i, schedule_datetime in enumerate(schedule_datetimes):
            schedule = android_schedule_time(SystemClock.elapsedRealtime(), schedule_datetime)
            # schedule = SystemClock.elapsedRealtime() + 1000 + i * 10000
            pi = PendingIntent.getBroadcast(activity, self.PENDING_INTENT_REQUEST_CODE + i, intent, 0)
            self.alarm_manager.setInexactRepeating(
                AlarmManager.ELAPSED_REALTIME_WAKEUP,
                schedule,
                AlarmManager.INTERVAL_DAY,
                pi
            )
            Logger.info("Notifications: scheduled notification: %s, %s" % (schedule_datetime, schedule))
