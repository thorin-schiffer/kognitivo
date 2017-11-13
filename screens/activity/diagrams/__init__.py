from kivy import Logger
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from library_widgets import TutorialMixin
from screens.activity.diagrams.base import BarStatsDiagram, FilledLineStatsDiagram, DiagramLabelsContainer, StatsDiagram
import settings
from utils import import_kv

import_kv(__file__)


class HourDiagramLabelsContainer(DiagramLabelsContainer):
    def format_x_label(self, value):
        return "[b]%02d[/b]:00" % value


class ActivityDayStats(TutorialMixin, BarStatsDiagram):
    POINT_VALUES = range(24)

    def get_percentages(self):
        from managers.database import database_manager
        return database_manager.hour_percents(self.family)


class ProgressDiagramLabelsContainer(DiagramLabelsContainer):
    def format_x_label(self, value):
        if not value:
            return super(ProgressDiagramLabelsContainer, self).format_x_label(value)

        from datetime import datetime

        date = datetime.strptime(str(int(value)), '%Y%j').date()
        return date.strftime('%m.%d')


class ProgressStats(TutorialMixin, FilledLineStatsDiagram):
    GROUP_BY_FIELD = "round(strftime('%%Y%%j', created))"

    def get_percentages(self):
        from managers.database import database_manager

        percents = database_manager.recent_percents(self.family)
        return {int(key.strftime('%Y%j')): value for key, value in percents.items()}

    def __init__(self):
        from datetime import datetime, timedelta
        self.POINT_VALUES = [int((datetime.now() - timedelta(days=13 - value)).strftime('%Y%j')) for value in range(14)]
        super(ProgressStats, self).__init__()


class WeekDiagramLabelsContainer(DiagramLabelsContainer):
    def format_x_label(self, value):
        return self.LABELS[value]

    def __init__(self, **kwargs):
        from utils import _

        self.LABELS = dict([(0, _("MO")),
                            (1, _("TU")),
                            (2, _("WE")),
                            (3, _("TH")),
                            (4, _("FR")),
                            (5, _("SA")),
                            (6, _("SU"))])

        super(WeekDiagramLabelsContainer, self).__init__(**kwargs)


class ActivityWeekStats(TutorialMixin, BarStatsDiagram):
    POINT_VALUES = range(7)
    LINE_WIDTH = dp(1.2)

    def get_percentages(self):
        from managers.database import database_manager
        return database_manager.day_percents(self.family)


class EfficiencyBar(ButtonBehavior, AnchorLayout):
    family = StringProperty(None, allownone=True)
    percentage = NumericProperty()
    label = ObjectProperty()
    _fill_color = ListProperty(settings.ACTIVITY_COLORS[None])
    _back_color = ListProperty(settings.ACTIVITY_COLORS_TRANSPARENT[None])

    def on_family(self, instance, value):
        from kivy.animation import Animation
        Animation(
            _back_color=settings.ACTIVITY_COLORS_TRANSPARENT[value],
            _fill_color=settings.ACTIVITY_COLORS[value],
            duration=.25, t='in_out_cubic'
        ).start(self)


class CalendarStatsEntry(BoxLayout):
    begin = ObjectProperty()
    end = ObjectProperty()
    all_day = BooleanProperty()
    title = StringProperty(allownone=True)
    calendar_id = StringProperty()
    efficiency = NumericProperty()
    family = StringProperty('', allownone=True)
    efficiency_bar = ObjectProperty()
    calendar_color = ListProperty()

    def on_calendar_id(self, *args):
        from managers.calendar import calendar_manager
        try:
            calendar = calendar_manager.get_calendars()[self.calendar_id]
        except KeyError:
            pass
        self.calendar_color = calendar['color']


class ListStats(TutorialMixin, StatsDiagram, ScrollView):
    family = StringProperty('', allownone=True)
    container = ObjectProperty()
    HOURS = range(24)
    DAYS = range(7)

    def build_entries(self, *args):
        raise NotImplementedError()

    def update_entries(self):
        raise NotImplementedError()

    def get_data(self):
        raise NotImplementedError()

    def update(self, *args, **kwargs):
        self.get_data()
        if not self.entries:
            self.build_entries()
        self.update_entries()

    def __init__(self, **kwargs):
        self.entries = []
        self.data = {}
        super(ListStats, self).__init__(**kwargs)


class CalendarStats(ListStats):
    def get_data(self):
        self.values = dict(zip(self.HOURS, [0] * len(self.HOURS)))
        self.data['hours'] = self.interpolated_values()
        self.values = dict(zip(self.DAYS, [0] * len(self.DAYS)))
        self.data['days'] = self.interpolated_values()

    def get_percentages(self):
        from managers.database import database_manager
        if self.values.keys() == self.HOURS:
            return database_manager.hour_percents(self.family)
        else:
            return database_manager.day_percents(self.family)

    def update_entries(self):
        from kivy.animation import Animation
        from datetime import datetime
        from utils import _
        billing = App.get_running_app().billing
        purchased_items = billing.get_purchased_items()
        if not settings.INAPP_PURCHASES:
            is_premium = True
        else:
            is_premium = 'lifetime_premium' in purchased_items or 'premium_subscription' in purchased_items

        for entry in self.entries:
            entry.family = self.family
            try:
                if not entry.all_day:
                    efficiency = self.data['hours'][entry.begin.hour] * .5
                    efficiency += self.data['days'][entry.begin.weekday()] * .5
                else:
                    efficiency = self.data['days'][entry.begin.weekday()]
            except KeyError:
                Logger.info("Calendar: key error in efficiency, set to 1...")
                efficiency = 2.
            if not is_premium and entry.begin > datetime.now():
                entry.efficiency_bar.label.text = _("GET PREMIUM")
                entry.efficiency_bar.on_press = lambda *args: billing.buy('lifetime_premium', callbacks=[self.update])
                entry.efficiency = 2.
            else:
                entry.efficiency_bar.on_press = lambda *args: None
                Animation(efficiency=efficiency, d=.5, t='in_out_cubic').start(entry)
                entry.efficiency_bar.label.text = "%.0f%%" % (efficiency * 100)

    def build_entries(self, *args):

        from managers.calendar import calendar_manager
        events = calendar_manager.get_events()
        if not events:
            Logger.info("Calendar: no events found...")
        else:
            self.container.clear_widgets()
        for event in events:
            entry = CalendarStatsEntry(
                family=self.family,
                **event)
            self.entries.append(entry)
            self.container.add_widget(entry)


class ActivityStatsEntry(BoxLayout):
    title = StringProperty()
    efficiency = NumericProperty()
    icon = StringProperty()
    family = StringProperty('', allownone=True)
    premium = BooleanProperty()
    weights = ListProperty()


class ActivityStats(ListStats):
    def get_percentages(self):
        from managers.database import database_manager
        if self.values.keys() == self.HOURS:
            return database_manager.hour_percents(self.current_family)
        else:
            return database_manager.day_percents(self.current_family)

    def get_data(self):
        from datetime import datetime
        now = datetime.now()
        for family in [
            settings.ANALYTICS_FAMILY,
            settings.ATTENTION_FAMILY,
            settings.REACTION_FAMILY,
            settings.MEMORY_FAMILY
        ]:
            self.current_family = family
            self.values = dict(zip(self.HOURS, [0] * len(self.HOURS)))
            hours = self.interpolated_values()
            self.values = dict(zip(self.DAYS, [0] * len(self.DAYS)))
            days = self.interpolated_values()
            try:
                self.data[family] = hours[now.hour] * .5 + days[now.weekday()] * .5
            except KeyError:
                self.data[family] = 1

    def __init__(self, **kwargs):
        super(ActivityStats, self).__init__(**kwargs)
        from utils import _
        # weights: a, t, r, m
        self.current_family = None
        self.config = [
            {
                "title": _("ANALYTICS"),
                "family": settings.ANALYTICS_FAMILY,
                "icon": "atlas://data/atlas/menu/analytics",
                "premium": False,
                "weights": [1., 0, 0, 0]
            },
            {
                "title": _("ATTENTION"),
                "family": settings.ATTENTION_FAMILY,
                "icon": "atlas://data/atlas/menu/attention",
                "premium": False,
                "weights": [0, 1., 0, 0]
            },
            {
                "title": _("REACTION"),
                "family": settings.REACTION_FAMILY,
                "icon": "atlas://data/atlas/menu/reaction",
                "premium": False,
                "weights": [0, 0, 1., 0]
            },
            {
                "title": _("MEMORY"),
                "family": settings.MEMORY_FAMILY,
                "icon": "atlas://data/atlas/menu/memory",
                "premium": False,
                "weights": [0, 0, 0, 1.]
            },
            {
                "title": _("reading"),
                "family": settings.MEMORY_FAMILY,
                "icon": "atlas://data/atlas/activity/reading",
                "premium": True,
                "weights": [0.4, 0.1, 0, 0.5]
            },
            {
                "title": _("writing"),
                "family": settings.ATTENTION_FAMILY,
                "icon": "atlas://data/atlas/activity/writing",
                "premium": True,
                "weights": [0.2, 0.1, 0, 0.7]
            },
            {
                "title": _("math"),
                "family": settings.ANALYTICS_FAMILY,
                "icon": "atlas://data/atlas/activity/math",
                "premium": True,
                "weights": [0.7, 0.2, 0, 0.2]
            },
            {
                "title": _("driving"),
                "family": settings.REACTION_FAMILY,
                "icon": "atlas://data/atlas/activity/driving",
                "premium": True,
                "weights": [.2, .4, .4, 0]
            },
            {
                "title": _("internet"),
                "family": settings.ATTENTION_FAMILY,
                "icon": "atlas://data/atlas/activity/internet",
                "premium": True,
                "weights": [.2, .4, 0, .4]
            },
            {
                "title": _("studying"),
                "family": settings.MEMORY_FAMILY,
                "icon": "atlas://data/atlas/activity/studying",
                "premium": True,
                "weights": [.1, .3, 0, .6]
            },
            {
                "title": _("navigation"),
                "family": settings.ANALYTICS_FAMILY,
                "icon": "atlas://data/atlas/activity/routes",
                "premium": True,
                "weights": [.6, .3, 0, .1]
            },
            {
                "title": _("languages"),
                "family": None,
                "icon": "atlas://data/atlas/activity/foreign_language",
                "premium": True,
                "weights": [.4, .1, 0, .5]
            },
            {
                "title": _("strategy games"),
                "family": settings.ANALYTICS_FAMILY,
                "icon": "atlas://data/atlas/activity/strategy_game",
                "premium": True,
                "weights": [.7, .1, .1, .1]
            },
            {
                "title": _("action games"),
                "family": settings.REACTION_FAMILY,
                "icon": "atlas://data/atlas/activity/action_game",
                "premium": True,
                "weights": [.1, .3, .6, 0]
            },
            {
                "title": _("quizzes"),
                "family": settings.MEMORY_FAMILY,
                "icon": "atlas://data/atlas/activity/quiz_game",
                "premium": True,
                "weights": [.1, .1, .2, .6]
            },
            {
                "title": _("arcades"),
                "family": settings.REACTION_FAMILY,
                "icon": "atlas://data/atlas/activity/arcade_game",
                "premium": True,
                "weights": [.3, .2, .4, .1]
            },
            {
                "title": _("puzzles"),
                "family": settings.ATTENTION_FAMILY,
                "icon": "atlas://data/atlas/activity/puzzle",
                "premium": True,
                "weights": [0.4, 0.5, 0, 0.1]
            },
            {
                "title": _("card games"),
                "family": settings.ANALYTICS_FAMILY,
                "icon": "atlas://data/atlas/activity/card_game",
                "premium": True,
                "weights": [.4, .3, 0, .3]
            },
            {
                "title": _("casual games"),
                "family": settings.MEMORY_FAMILY,
                "icon": "atlas://data/atlas/activity/casual_game",
                "premium": True,
                "weights": [.4, .3, .3, .1]
            },
            {
                "title": _("racing games"),
                "family": settings.REACTION_FAMILY,
                "icon": "atlas://data/atlas/activity/race_game",
                "premium": True,
                "weights": [.1, .3, .6, 0]
            },
            {
                "title": _("word games"),
                "family": settings.MEMORY_FAMILY,
                "icon": "atlas://data/atlas/activity/word_game",
                "premium": True,
                "weights": [.2, .1, 0, .7]
            }
        ]

    def update_entries(self):
        from kivy.animation import Animation
        from utils import _
        from billing.abstract import BillingException
        billing = App.get_running_app().billing
        purchased_items = billing.get_purchased_items()
        if not settings.INAPP_PURCHASES:
            is_premium = True
        else:
            is_premium = 'lifetime_premium' in purchased_items or 'premium_subscription' in purchased_items

        efficiencies = {}
        for entry in self.entries:
            efficiency = sum(self.data[family] * entry.weights[i] for i, family in enumerate(
                [
                    settings.ANALYTICS_FAMILY,
                    settings.ATTENTION_FAMILY,
                    settings.REACTION_FAMILY,
                    settings.MEMORY_FAMILY
                ]
            ))
            if not is_premium and entry.premium:
                efficiencies[entry] = 0
                entry.efficiency_bar.label.text = _("GET PREMIUM")
                try:
                    entry.efficiency_bar.on_press = lambda *args: billing.buy('lifetime_premium',
                                                                              callbacks=[self.update])
                except BillingException:
                    pass
                entry.efficiency = 2
            else:
                efficiencies[entry] = efficiency
                entry.efficiency_bar.on_press = lambda *args: None
                Animation(efficiency=efficiency, d=.5, t='in_out_cubic').start(entry)
                entry.efficiency_bar.label.text = "%.0f%%" % (efficiency * 100)
        self.container.children = sorted(self.container.children, key=lambda e: efficiencies[e])

    def build_entries(self, *args):
        self.container.clear_widgets()
        for c in self.config:
            entry = ActivityStatsEntry(**c)
            self.entries.append(entry)
            self.container.add_widget(entry)
