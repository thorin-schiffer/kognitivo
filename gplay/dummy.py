from gplay.abstract import AbstractGoogleClient


class DummyGoogleClient(AbstractGoogleClient):
    def __init__(self):
        super(DummyGoogleClient, self).__init__()
        self.client = self._get_client()
        self.connected = False

    def connect(self, success_callback=None, fail_callback=None):
        super(DummyGoogleClient, self).connect(success_callback=None, fail_callback=None)
        self.connected = True
        if success_callback:
            success_callback()

    def is_connected(self):
        super(DummyGoogleClient, self).is_connected()
        return self.connected

    def logout(self):
        super(DummyGoogleClient, self).logout()
        self.connected = False

    def show_achievements(self):
        super(DummyGoogleClient, self).show_achievements()
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        popup = Popup(title="DUMMY ACHIEVEMENTS", content=Label(text='Achievements achieved'))
        popup.open()

    def show_leaderboard(self, name):
        super(DummyGoogleClient, self).show_leaderboard(name)
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label

        popup = Popup(title="DUMMY LEADERBOARD", content=Label(text=name))
        popup.open()
