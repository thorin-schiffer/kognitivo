from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, ListProperty, NumericProperty, \
    OptionProperty
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanelItem

from library_widgets import TutorialMixin, ColorSquare

from utils import _, import_kv  # noqa F401
# do not remove
# noinspection PyUnresolvedReferences
import diagrams  # noqa F401

import_kv(__file__)


class LikePopup(Popup):
    def store_feedback(self, value):
        storage = App.get_running_app().storage
        storage['facebook_like'] = {"status": value}
        app = App.get_running_app()
        if value:
            app.tracker.send_event('clicks', 'fb_like_popup', 'accepted')
            app.google_client.unlock_achievement("social_contributor")
        else:
            app.tracker.send_event('clicks', 'fb_like_popup', 'rejected')


class RatePopup(Popup):
    def store_feedback(self, value):
        storage = App.get_running_app().storage
        storage['feedback'] = {"status": value}
        app = App.get_running_app()
        if value:
            app.tracker.send_event('clicks', 'rate_popup', 'accepted')
            app.google_client.unlock_achievement("supporter")
        else:
            app.tracker.send_event('clicks', 'rate_popup', 'rejected')


class FilterPanel(TutorialMixin, ColorSquare, BoxLayout):
    buttons = ObjectProperty()
    family = StringProperty('', allownone=True)
    state = OptionProperty('closed', options=['closed', 'open'])

    def toggle(self):
        from kivy.animation import Animation
        if self.state == 'closed':
            self.state = 'open'
            Animation(pos_hint={"x": .55, "center_y": .5}, t='in_out_cubic', d=.5).start(self)
        else:
            self.state = 'closed'
            Animation(pos_hint={"x": 1, "center_y": .5}, t='in_out_cubic', d=.5).start(self)


class FilterButton(ButtonBehavior, Image):
    family = StringProperty(None, allownone=True)
    background_color = ListProperty()
    color = ListProperty()
    font_size = NumericProperty()
    image_scale = NumericProperty(1)

    def on_press(self):
        super(FilterButton, self).on_press()
        self.filter_panel.toggle()
        App.get_running_app().manager.get_screen('activity').family = self.family


class StatsPanel(FloatLayout):
    family = StringProperty(' ', allownone=True)
    start_button = ObjectProperty()
    tab_panel = ObjectProperty()
    filter_panel = ObjectProperty()

    def on_family(self, instance, value):
        self.filter_panel.family = value
        for tab in self.tab_panel.tab_list:
            tab.family = value

    def update(self):
        for tab in self.tab_panel.tab_list:
            tab.update()


class DiagramsTabbedPanelItem(TabbedPanelItem):
    family = StringProperty(' ', allownone=True)
    container = ObjectProperty()
    diagram = ObjectProperty()
    filterable = BooleanProperty(True)

    def update(self):
        if self.parent.tabbed_panel.current_tab == self:
            self.diagram.update()

    def on_family(self, instance, value):
        import settings
        from kivy.animation import Animation

        Animation(background_color_down=settings.ACTIVITY_COLORS[value], d=.5).start(self)
        self.diagram.family = value
        self.update()

    def get_diagram(self):  # pragma: no cover
        raise NotImplementedError()

    def on_container(self, *args, **kwargs):
        self.diagram = self.get_diagram()
        self.container.add_widget(self.diagram)


class DaysStatsTabbedPanelItem(DiagramsTabbedPanelItem):
    def get_diagram(self):
        from screens.activity.diagrams import ActivityDayStats

        return ActivityDayStats()


class WeekStatsTabbedPanelItem(DiagramsTabbedPanelItem):
    def get_diagram(self):
        from screens.activity.diagrams import ActivityWeekStats

        return ActivityWeekStats()


class ProgressStatsTabbedPanelItem(DiagramsTabbedPanelItem):
    def get_diagram(self):
        from screens.activity.diagrams import ProgressStats

        return ProgressStats()


class CalendarStatsTabbedPanelItem(DiagramsTabbedPanelItem):
    def get_diagram(self):
        from screens.activity.diagrams import CalendarStats

        return CalendarStats()


class ActivityStatsTabbedPanelItem(DiagramsTabbedPanelItem):
    def get_diagram(self):
        from screens.activity.diagrams import ActivityStats

        return ActivityStats()


class FilterToggleButton(AnchorLayout):
    def hide(self):
        from kivy.animation import Animation
        Animation(opacity=0, d=.2, t='in_out_cubic').start(self)
        if self.parent.filter_panel.state == 'open':
            self.parent.filter_panel.toggle()

    def show(self):
        from kivy.animation import Animation
        Animation(opacity=1, d=.2, t='in_out_cubic').start(self)

    def open_filter(self):
        self.parent.filter_panel.toggle()
