from kivy import platform

from managers.calendar.dummy import DummyCalendarManager

if platform == 'android':
    from managers.calendar.android_calendar import AndroidCalendarManager

    calendar_manager = AndroidCalendarManager()
else:
    calendar_manager = DummyCalendarManager()
