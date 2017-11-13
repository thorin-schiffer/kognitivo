from kivy import Logger


class AbstractGoogleClient(object):
    def __init__(self):
        self.client = self._get_client()

    def _get_client(self):
        return None

    def connect(self, success_callback=None, fail_callback=None):
        Logger.info('Google: connecting...')

    def logout(self):
        Logger.info('Google: log out...')

    def is_connected(self):
        pass

    def unlock_achievement(self, name):
        Logger.info('Google: unlocked achievement %s' % name)

    def increment_achievement(self, name):
        Logger.info('Google: incremented achievement %s' % name)

    def show_achievements(self):
        Logger.info('Google: achievements shown')

    def submit_score(self, name, score):
        Logger.info('Google: score %s submitted to leaderboard %s' % (name, score))

    def show_leaderboard(self, name):
        Logger.info('Google: leaderboard %s shown' % name)
