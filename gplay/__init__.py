from kivy.utils import platform

from gplay.dummy import DummyGoogleClient

if platform == 'android':
    from gplay.android_gplay import AndroidGoogleClient

    GoogleClient = AndroidGoogleClient
else:
    GoogleClient = DummyGoogleClient
