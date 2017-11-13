from kivy import Logger

from managers.facebook.abstract import AbstractFacebookManager
from jnius import autoclass, JavaException

python_activity = autoclass('org.kivy.android.PythonActivity').mActivity
Context = autoclass('android.content.Context')
AppEventsLogger = autoclass('com.facebook.appevents.AppEventsLogger')
FacebookSdk = autoclass('com.facebook.FacebookSdk')


class AndroidFacebookManager(AbstractFacebookManager):
    def activate(self):
        super(AndroidFacebookManager, self).activate()
        try:
            AppEventsLogger.activateApp(python_activity)
        except JavaException as ex:
            Logger.error("Facebook Android: %s" % ex)

    def deactivate(self):
        super(AndroidFacebookManager, self).deactivate()
        try:
            AppEventsLogger.deactivateApp(python_activity)
        except JavaException as ex:
            Logger.error("Facebook Android: %s" % ex)

    def initialize(self):
        super(AndroidFacebookManager, self).initialize()
        try:
            FacebookSdk.sdkInitialize(python_activity.getApplicationContext())
        except JavaException as ex:
            Logger.error("Facebook Android: %s" % ex)
