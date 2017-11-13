from kivy import platform
from managers.facebook.dummy import DummyFacebookManager

if platform == 'android':
    from managers.facebook.android_facebook import AndroidFacebookManager

    facebook_manager = AndroidFacebookManager()
else:
    facebook_manager = DummyFacebookManager()
