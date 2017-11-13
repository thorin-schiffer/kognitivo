from kivy import Logger
from jnius import PythonJavaClass, autoclass, java_method, JavaException
# noinspection PyUnresolvedReferences
from android import activity
import settings
from gplay.abstract import AbstractGoogleClient

Builder = autoclass("com.google.android.gms.common.api.GoogleApiClient$Builder")
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Plus = autoclass("com.google.android.gms.plus.Plus")
Games = autoclass("com.google.android.gms.games.Games")

Rstring = autoclass("android.R$string")
Rid = autoclass("android.R$id")


class GoogleApiClientConnectionCallback(PythonJavaClass):
    __javainterfaces__ = ['com.google.android.gms.common.api.GoogleApiClient$ConnectionCallbacks',
                          'com.google.android.gms.common.api.GoogleApiClient$OnConnectionFailedListener']
    __javacontext__ = 'app'
    RC_SIGN_IN = 9001
    RC_RESOLUTION = 1001
    RESULT_OK = -1
    RESULT_CANCELLED = 0
    REQUEST_ACHIEVEMENTS = 1
    REQUEST_LEADERBOARDS = 2

    def __init__(self):
        super(GoogleApiClientConnectionCallback, self).__init__()
        self.on_connected_callback = None
        self.resolving_failure_callback = None
        self.in_resolving_connection = False

    @java_method('(Landroid/os/Bundle;)V')
    def onConnected(self, connectionHint):
        Logger.info("Google: successfully logged in")
        Games.setViewForPopups(self.client,
                               PythonActivity.mActivity.getWindow().getDecorView().findViewById(Rid.content))
        Logger.info("Google: set view for popup")

        if self.on_connected_callback:
            self.on_connected_callback()

    def on_activity_result(self, requestCode, resultCode, intent):
        Logger.info("Google: back to activity result. %s, %s" % (requestCode, resultCode))
        if requestCode == self.RC_RESOLUTION:
            self.in_resolving_connection = False
            if resultCode == self.RESULT_OK:
                Logger.info("Google: resolving result okay")
                self.client.connect()
            elif resultCode == self.RESULT_CANCELLED:
                Logger.info("Google: resolving cancelled")
            else:
                Logger.warning("Google: resolving failed. Error code: %s" % resultCode)
                if self.resolving_failure_callback:
                    self.resolving_failure_callback(resultCode)

    @java_method('(Lcom/google/android/gms/common/ConnectionResult;)V')
    def onConnectionFailed(self, connectionResult):
        Logger.info(
            "Google: connection failed. Error code: %s. Trying to resolve..." % connectionResult.getErrorCode())

        if self.in_resolving_connection:
            Logger.info("Google: already in resolving, pass...")
            return

        self.in_resolving_connection = True

        if connectionResult.hasResolution():
            Logger.info("Google: starting resolution...")
            activity.bind(on_activity_result=self.on_activity_result)
            connectionResult.startResolutionForResult(PythonActivity.mActivity, self.RC_RESOLUTION)
        else:
            Logger.info("Google: connection issue has no resolution... "
                        "hasResolution says: %s" % connectionResult.hasResolution())

    @java_method('(I)V')
    def onConnectionSuspended(self, i):
        raise Exception("JAVA callback onConnectionSuspended wrap success")

    @java_method('()I')
    def hashCode(self):
        # hack because of the python and c long type error
        return (id(self) % 2147483647)

    @java_method('()Ljava/lang/String;', name='hashCode')
    def hashCode_(self):
        return '{}'.format(id(self))

    @java_method('(Ljava/lang/Object;)Z')
    def equals(self, obj):
        return obj.hashCode() == self.hashCode()


class AndroidGoogleClient(AbstractGoogleClient):
    def __init__(self):
        try:
            self.app = PythonActivity.getApplication()
            super(AndroidGoogleClient, self).__init__()
        except JavaException:
            self.app = None
            self.client = None
            import settings

            if settings.DEVELOPMENT_VERSION:
                raise

    def _get_client(self):
        try:
            Logger.info("Google: building client...")
            self.connection_callback = GoogleApiClientConnectionCallback()
            mGoogleApiClient = Builder(self.app). \
                addConnectionCallbacks(self.connection_callback). \
                addOnConnectionFailedListener(self.connection_callback). \
                addApi(Plus.API).addScope(Plus.SCOPE_PLUS_LOGIN). \
                addApi(Games.API).addScope(Games.SCOPE_GAMES).build()
            self.connection_callback.client = mGoogleApiClient
        except JavaException:
            import settings

            if settings.DEVELOPMENT_VERSION:
                raise
            else:
                return None
        return mGoogleApiClient

    def connect(self, success_callback=None, fail_callback=None):
        super(AndroidGoogleClient, self).connect()
        if self.client:
            self.connection_callback.on_connected_callback = success_callback
            self.connection_callback.resolving_failure_callback = fail_callback
            try:
                self.client.connect()
            except JavaException:
                self.client = None

    def logout(self):
        super(AndroidGoogleClient, self).logout()
        if self.client and self.is_connected():
            try:
                Games.signOut(self.client)
                self.client = None
            except JavaException:
                Logger.error("Google: error while logout")

    def is_connected(self):
        super(AndroidGoogleClient, self).is_connected()
        if self.client:
            is_connected = self.client.isConnected()
            Logger.info('Google: is connected %s' % is_connected)
            return is_connected
        else:
            return False

    def unlock_achievement(self, name):
        if self.client and self.is_connected():
            Logger.info('Google: unlocked achievement %s' % name)
            try:
                Games.Achievements.unlock(self.client, settings.GOOGLE_PLAY_ACHIEVEMENT_IDS[name])
            except JavaException:
                Logger.warning("Google: error while unlocking achievement, pass...")
        else:
            Logger.info("Google: achievement is not submitted. Client: %s, is connected: %s" % (
                self.client, self.is_connected()))

    def increment_achievement(self, name, value=1):
        if self.client and self.is_connected():
            Logger.info('Google: incremented achievement %s' % name)
            try:
                Games.Achievements.increment(self.client, settings.GOOGLE_PLAY_ACHIEVEMENT_IDS[name], value)
            except JavaException:
                Logger.warning("Google: error while increment achievement, pass...")
        else:
            Logger.info("Google: achievement is not submitted. Client: %s, is connected: %s" % (
                self.client, self.is_connected()))

    def show_achievements(self):
        if self.client and self.is_connected():
            PythonActivity.mActivity.startActivityForResult(Games.Achievements.getAchievementsIntent(self.client),
                                                            GoogleApiClientConnectionCallback.REQUEST_ACHIEVEMENTS)

    def submit_score(self, name, score):
        if self.client and self.is_connected():
            Logger.info('Google: submit score %s to %s' % (score, name))
            Games.Leaderboards.submitScore(self.client, settings.GOOGLE_PLAY_LEADERBOARD_IDS[name], score)
        else:
            Logger.info("Google: score is not submitted. Client: %s, is connected: %s" % (
                self.client, self.is_connected()))

    def show_leaderboard(self, name):
        if self.client and self.is_connected():
            PythonActivity.mActivity.startActivityForResult(
                Games.Leaderboards.getLeaderboardIntent(
                    self.client,
                    settings.GOOGLE_PLAY_LEADERBOARD_IDS[name]
                ), GoogleApiClientConnectionCallback.REQUEST_LEADERBOARDS)
