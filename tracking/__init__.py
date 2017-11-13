from kivy.utils import platform

from tracking.dummy import DummyTracker

if platform == 'android':
    from tracking.android_tracking import GoogleTracker

    Tracker = GoogleTracker
else:
    Tracker = DummyTracker
