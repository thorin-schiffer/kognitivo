from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout

from kivy.properties import StringProperty, ListProperty, NumericProperty, ObjectProperty, OptionProperty

from screens.navigator import NavigationDrawer
from utils import import_kv

import_kv(__file__)


class Menu(RelativeLayout):
    buttons_container = ObjectProperty()
    purchase_button = ObjectProperty()
    gp_achievements_button = ObjectProperty()
    gp_leaderboard_button = ObjectProperty()

    def on_buttons_container(self, screen, container):
        import settings
        if settings.INAPP_PURCHASES:
            self.purchase_button = PurchaseButton()
            container.add_widget(self.purchase_button)

        if settings.GOOGLE_PLAY_ACHIEVEMENT_IDS:
            self.gp_achievements_button = GooglePlayAchievementsButton()
            container.add_widget(self.gp_achievements_button)

        if settings.LEADERBOARD:
            self.gp_leaderboard_button = GooglePlayLeaderboardButton()
            container.add_widget(self.gp_leaderboard_button)


class MenuButtonTitled(ButtonBehavior, Image):
    point_activity = StringProperty(None, allownone=True)
    point_screen = StringProperty('activity')
    background_color = ListProperty()
    color = ListProperty()
    font_size = NumericProperty()
    image_scale = NumericProperty(1)
    image_pos = OptionProperty('right', options=['right', 'center'])

    def on_press(self):
        nav = App.get_running_app().root
        if nav:
            nav.bind(state=self.to_screen)
            nav.toggle_state()
        else:
            self.to_screen()

    def to_screen(self, *_):
        app = App.get_running_app()
        app.sounds['tap'].play()
        nav = app.root
        if nav:
            nav.unbind(state=self.to_screen)
        manager = app.manager
        manager.to_screen(self.point_screen)


class MoreAppsButton(MenuButtonTitled):
    pass


class GoogleConnectMenuButton(MenuButtonTitled):
    def dispatch_connect(self, *args, **kwargs):
        self.dispatch('on_connect')

    def on_press(self):
        super(GoogleConnectMenuButton, self).on_press()
        if not App.get_running_app().google_client.is_connected():
            App.get_running_app().google_client.connect(success_callback=self.dispatch_connect)
        else:
            self.dispatch_connect()

    def __init__(self, *args, **kwargs):
        self.register_event_type('on_connect')
        super(GoogleConnectMenuButton, self).__init__(*args, **kwargs)

    def on_connect(self):
        pass


class GooglePlayAchievementsButton(GoogleConnectMenuButton):
    pass


class GooglePlayLeaderboardButton(GoogleConnectMenuButton):
    pass


class PurchaseButton(MenuButtonTitled):
    pass


class SettingsButton(MenuButtonTitled):
    def on_press(self, *_):
        App.get_running_app().open_settings()


class MenuToggleButton(AnchorLayout):
    def hide(self):
        from kivy.animation import Animation
        Animation(opacity=0, d=.2, t='in_out_cubic').start(self)

    def show(self):
        from kivy.animation import Animation
        Animation(opacity=1, d=.2, t='in_out_cubic').start(self)


class KognitivoNavigator(NavigationDrawer):
    toggle = ObjectProperty()

    def __init__(self, **kwargs):
        super(KognitivoNavigator, self).__init__(**kwargs)
        self.toggle = MenuToggleButton()

    def anim_to_state(self, state):
        if state == 'closed':
            self.toggle.show()
        else:
            self.toggle.hide()

        super(KognitivoNavigator, self).anim_to_state(state)

    def attach_toggle(self, window):
        window.add_widget(self.toggle)
