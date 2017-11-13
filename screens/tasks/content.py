from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, SlideTransition, Screen
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.app import App, platform
from kivy.logger import Logger
import settings

from utils import _, import_kv
from library_widgets import CircleDiagram, ImageButton, DidYouKnowLabel

import_kv(__file__)


class TaskIcon(Image):
    is_complete = BooleanProperty(False)
    complete_source = StringProperty()
    incomplete_source = StringProperty()
    task_class = ObjectProperty()

    def change_source(self, *_):
        from kivy.animation import Animation

        if self.is_complete:
            self.source = self.complete_source
        else:
            self.source = self.incomplete_source
        Animation(opacity=1, duration=.2, t='in_out_sine').start(self)

    def on_complete(self, instance, complete):
        from kivy.animation import Animation

        animation = Animation(opacity=0, duration=.3, t='in_out_sine')
        animation.bind(on_complete=self.change_source)
        animation.start(self)

    def on_task_class(self, icon, klass):
        self.incomplete_source = "atlas://data/atlas/tasks/%s" % klass
        self.source = self.incomplete_source

    def __init__(self, **kwargs):
        super(TaskIcon, self).__init__(**kwargs)
        self.bind(is_complete=self.on_complete)
        self.source = self.incomplete_source
        self.selected = False


class TestOutroDiagramLabel(Label):
    pass


class TestOutro(Screen):
    day_diagram = ObjectProperty()
    week_diagram = ObjectProperty()
    points = NumericProperty()
    diagrams_container = ObjectProperty()

    day_efficiency = NumericProperty()
    week_efficiency = NumericProperty()

    status_label = ObjectProperty()
    status_image = ObjectProperty()

    status_container = ObjectProperty()

    def on_enter(self, *args):
        App.get_running_app().sounds['test_finished'].play()

    def on_day_efficiency(self, outro, value):
        self.day_diagram.part = value
        self.on_points()

    def on_week_efficiency(self, outro, value):
        self.week_diagram.part = value

    def __init__(self, **kwargs):
        super(TestOutro, self).__init__(**kwargs)
        self.RANGES = {
            50: _("Typing monkey"),
            60: _("Homo erectus"),
            70: _("Slowpoke"),
            80: _("Homo sapiens"),
            90: _("Junkie"),
            100: _("Mr Perfect"),
            110: _("Genius"),
            120: _("Nerd"),
            130: _("Holmes"),
            140: _("Einstein"),
            150: _("Kognimaster")
        }

    def _get_marker(self):
        marker = 10 * (int(100 * self.day_diagram.part) / 10)
        marker = min(marker, 150)
        marker = max(marker, 50)
        return marker

    def on_points(self, *args, **kwargs):
        marker = self._get_marker()
        self.status_label.text = self.RANGES[marker].upper() + "\n" + _(
            "[size=20sp][color=#6666660A]%s POINTS[/color][/size]"
        ) % self.points
        self.status_image.source = "data/img/status_icons/icon_%s.png" % marker

    def on_diagrams_container(self, instance, value):
        self.day_diagram = CircleDiagram()
        self.week_diagram = CircleDiagram()
        self.diagrams_container.add_widget(self.day_diagram)
        self.diagrams_label_container.add_widget(TestOutroDiagramLabel(text=_("of your\n[b]Day's[/b] average")))

        from managers.database import database_manager
        if database_manager.total_time().days > 7:
            self.diagrams_container.add_widget(self.week_diagram)
            self.diagrams_label_container.add_widget(TestOutroDiagramLabel(text=_("of your\n[b]Week's[/b] average")))

    def share(self):
        if platform == 'android':
            from jnius import autoclass, cast
            Context = autoclass('android.content.Context')
            File = autoclass('java.io.File')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            AndroidString = autoclass('java.lang.String')

            import uuid
            file_ = File(Context.getCacheDir(), "share-%s.png" % uuid.uuid4())

            from utils import export_to_png
            path = file_.getPath()
            export_to_png(self.status_container, path, (1, 1, 1, 1))
            file_.setReadable(True, False)

            Logger.info("Sharing: share %s" % path)

            intent = Intent()
            intent.setAction(Intent.ACTION_SEND)
            text = (_("My cognitive status #kognitivo #braintrainer %s") % settings.STORE_URL).encode('utf-8')
            intent.putExtra(Intent.EXTRA_SUBJECT, "Sharing File...")
            intent.putExtra(Intent.EXTRA_TEXT, text)
            parcelable = cast('android.os.Parcelable', Uri.parse(path))
            intent.putExtra(Intent.EXTRA_STREAM, parcelable)

            intent.setType(AndroidString('image/png'))
            chooser = Intent.createChooser(intent, AndroidString("Sharing File..."))
            PythonActivity.mActivity.startActivity(chooser)


class PointsLabel(Label):
    points = NumericProperty(0)

    def on_points(self, instance, value):
        self.text = _("BEST RESULT: [b]%s[/b] POINTS") % value


class SessionTasksCounter(Label):
    counter = NumericProperty(-1)
    full_count = NumericProperty(4)

    def on_counter(self, instance, value):
        self.text = _(u"[color=#408742ff][font=glyphicons]\uE006[/font][/color] task #%(counter)s/%(full)s") % {
            "counter": self.counter,
            "full": self.full_count
        }


class TestStatus(BoxLayout):
    task_number = NumericProperty()
    task = StringProperty()
    task_number_widget = ObjectProperty()
    best_points_widget = ObjectProperty()
    full_count = NumericProperty(4)

    def on_task(self, status, task_key):
        app = App.get_running_app()
        self.best_points_widget.points = app.storage["task_records"][task_key]

    def on_task_number(self, status, value):
        self.task_number_widget.counter = value

    def on_full_count(self, status, value):
        self.task_number_widget.full_count = value


class TaskFinished(ImageButton):
    pass


class TestScreen(Screen):
    icon = ObjectProperty()
    task_container = ObjectProperty()
    status = ObjectProperty()
    task_number = NumericProperty()
    points = NumericProperty()

    def __init__(self, **kwargs):
        self.family = None
        self.task_classes = {}
        self.day_efficiency = 0
        self.week_efficiency = 0
        self.task_classes_in_session = []
        self.random = False
        super(TestScreen, self).__init__(**kwargs)
        self.transition = SlideTransition()

    @property
    def current_task(self):
        return self.task_container.children[0] if self.task_container.children else None

    def on_task_finished(self, task, successful):
        from managers.database import database_manager
        import settings
        import datetime
        self.task_classes_in_session = []
        self.icon.is_complete = True
        self.points += task.points
        storage = App.get_running_app().storage
        if storage["task_records"][task.TASK_KEY] < task.points:
            data = storage["task_records"]
            data.update({task.TASK_KEY: task.points})
            storage.put("task_records", **data)
            self.status.on_task(self.status, task.TASK_KEY)

        today = datetime.datetime.now()
        day_average = database_manager.task_efficiency_for_weekday(task.TASK_KEY, today.weekday())
        week_average = database_manager.task_efficiency_for_interval(task.TASK_KEY, today - datetime.timedelta(days=7),
                                                                     today)
        if day_average is None:
            self.day_efficiency += settings.LOW_DATA_EFFICIENCY_SCALE * task.efficiency
        else:
            self.day_efficiency += task.efficiency / (day_average * self.status.full_count)

        if week_average is None:
            self.week_efficiency += settings.LOW_DATA_EFFICIENCY_SCALE * task.efficiency
        else:
            self.week_efficiency += task.efficiency / (week_average * self.status.full_count)

        self.add_finished_marker(task)

    def to_test_outro(self, *args, **kwargs):
        if self.manager:
            self.manager.day_efficiency = self.day_efficiency
            self.manager.week_efficiency = self.week_efficiency
            self.manager.points = self.points
            self.manager.current = 'outro'
        from settings import LEADERBOARD
        app = App.get_running_app()
        sessions_finished = app.storage['sessions']['finished']

        app.tracker.send_event('tasks', 'sessions', label='finished', value=sessions_finished + 1)
        app.storage['sessions'] = {"started": app.storage['sessions']['started'],
                                   "finished": sessions_finished + 1}
        app.google_client.submit_score(LEADERBOARD, self.points)

    def add_finished_marker(self, task):
        task.clear_widgets()

        if self.task_number < self.status.full_count:
            next_task_button = TaskFinished(source="data/img/buttons/next_button.png")
            next_task_button.bind(on_press=self.load_next_task)
        else:
            next_task_button = TaskFinished(source="data/img/buttons/to_summary_button.png")
            next_task_button.bind(on_press=self.to_test_outro)

        outer_container = BoxLayout(orientation='vertical', size_hint_y=.5, size_hint_x=.8, padding=(0, 0, 0, dp(100)))
        outer_container.add_widget(DidYouKnowLabel())
        outer_container.add_widget(next_task_button)
        task.add_widget(outer_container)

    def animate_task_icon(self, *_):
        from kivy.animation import Animation

        old_y = self.icon.y
        self.icon.y = self.icon.parent.center[1] + self.icon.parent.height
        animation = Animation(y=old_y,
                              opacity=1,
                              duration=.3,
                              t='out_back')
        animation.start(self.icon)

    def start_test(self, family=None, tasks=None):
        self.prepare_task_classes(family, tasks)
        self.task_number = 0
        self.points = 0
        from kivy.animation import Animation

        self.load_next_task()
        animation = Animation(opacity=1, duration=.5, t='in_out_sine')
        animation.bind(on_complete=self.animate_task_icon)
        animation.start(self.task_container)

    @staticmethod
    def get_task_classes(family=None):
        import settings

        active_tasks = settings.TASKS.keys()
        billing = App.get_running_app().billing
        purchased_items = billing.get_purchased_items()
        Logger.info("Tasks: purchased items: %s" % purchased_items)

        premium_status = any(
            settings.INAPP_PURCHASES[purchased_item]['unlocks_tasks'] is None for
            purchased_item in purchased_items
        )
        if not premium_status:
            purchased_tasks = []
            for sku in purchased_items:
                purchased_tasks += settings.INAPP_PURCHASES[sku]['unlocks_tasks']
            purchased_tasks = list(set(purchased_tasks))

            active_tasks = [key for key in active_tasks if
                            not settings.TASKS[key]['purchasable'] or key in purchased_tasks]

        if family is not None:
            active_tasks = [key for key in active_tasks if family in settings.TASKS[key]['families']]
        Logger.info("Tasks: registered %s task classes" % len(active_tasks))
        return active_tasks

    def prepare_task_classes(self, family=None, task_classes=None):
        self.family = family
        if task_classes:
            self.task_classes = task_classes
            self.status.full_count = len(task_classes)
            self.random = False
        else:
            self.task_classes = self.get_task_classes(family=family)
            self.status.full_count = settings.TASKS_PER_TEST
            self.random = True

    def get_next_task_class(self):
        import random
        import importlib
        import settings

        if self.random:
            self.prepare_task_classes(self.family)
            if self.family is None:
                filter_family = [
                    settings.ANALYTICS_FAMILY,
                    settings.ATTENTION_FAMILY,
                    settings.REACTION_FAMILY,
                    settings.MEMORY_FAMILY
                ][self.task_number % 4]
                next_class = settings.TASKS[random.choice(
                    [
                        task_class for task_class in self.task_classes
                        if filter_family in settings.TASKS[task_class]['families'] and
                        task_class not in self.task_classes_in_session
                    ]
                )]['class']
            else:
                next_class = settings.TASKS[random.choice(self.task_classes)]['class']
        else:
            next_class = settings.TASKS[self.task_classes[self.task_number]]['class']
        self.task_classes_in_session.append(next_class)
        module, klass = next_class.rsplit(".", 1)
        next_class = getattr(importlib.import_module(module), klass)
        return next_class

    def on_task_number(self, screen, number):
        self.status.task_number = number

    def load_next_task(self, *args, **kwargs):
        self.task_container.clear_widgets()
        klass = self.get_next_task_class()
        self.status.task = klass.TASK_KEY
        self.icon.task_class = klass.TASK_KEY
        self.icon.is_complete = False
        task = klass(name="%s:%s" % (klass.TASK_KEY, self.task_number))
        task.bind(successful=self.on_task_finished)
        self.task_container.add_widget(task)
        self.task_number += 1
        Logger.info("Tasks: created %s" % klass)


class TaskScreenManager(ScreenManager):
    test_screen = ObjectProperty()
    day_efficiency = NumericProperty()
    week_efficiency = NumericProperty()
    points = NumericProperty()
    outro = ObjectProperty()
    task_sets_screen = ObjectProperty()

    def start_test(self, family=None, tasks=None):
        self.test_screen.start_test(family, tasks)
        self.current = 'test'

    def on_day_efficiency(self, manager, value):
        self.outro.day_efficiency = value

    def on_week_efficiency(self, manager, value):
        self.outro.week_efficiency = value

    def on_points(self, manager, value):
        self.outro.points = value


class TaskEntry(BoxLayout):
    task_key = StringProperty()


class TaskSet(BoxLayout):
    title = StringProperty()
    icon = StringProperty()
    tasks = ListProperty()
    tasks_container = ObjectProperty()
    color = ListProperty(settings.FILL_COLOR)
    buy = BooleanProperty(True)
    purchases_needed = ListProperty()
    screen = ObjectProperty()
    play_button = ObjectProperty()

    def on_tasks_container(self, *args):
        for task_key in self.tasks:
            entry = TaskEntry(task_key=task_key)
            self.tasks_container.add_widget(entry)

        if not self.needs_buy():
            self.play_button.text = _("PLAY")
        else:
            if self.purchases_needed and self.purchases_needed[0] != 'lifetime_premium':
                self.play_button.text = _("BUY")
            else:
                self.play_button.text = _("GET PREMIUM")

    def needs_buy(self):
        if not self.purchases_needed:
            return
        billing = App.get_running_app().billing
        purchased_items = billing.get_purchased_items()
        return not any(purchase in purchased_items for purchase in self.purchases_needed)

    def play(self, *args):
        if not self.needs_buy():
            main_manager = self.screen.manager
            main_manager.start_test(tasks=self.tasks)
        else:
            from billing.abstract import BillingException
            billing = App.get_running_app().billing
            try:
                billing.buy(self.purchases_needed[0], callbacks=[self.screen.fill])
            except BillingException:
                pass


class TaskSetsScreen(Screen):
    sets = ListProperty()
    container = ObjectProperty()

    def get_config(self):
        return [
            {
                "title": _("ANALYTICS"),
                "icon": "atlas://data/atlas/menu/analytics",
                "tasks": [
                    key for key, config in settings.TASKS.items()
                    if settings.ANALYTICS_FAMILY in config['families'] and not config['purchasable']
                ],
                "color": settings.ACTIVITY_COLORS[settings.ANALYTICS_FAMILY],
            },
            {
                "title": _("ATTENTION"),
                "icon": "atlas://data/atlas/menu/attention",
                "tasks": [
                    key for key, config in settings.TASKS.items()
                    if settings.ATTENTION_FAMILY in config['families'] and not config['purchasable']
                ],
                "color": settings.ACTIVITY_COLORS[settings.ATTENTION_FAMILY],
            },
            {
                "title": _("REACTION"),
                "icon": "atlas://data/atlas/menu/reaction",
                "tasks": [
                    key for key, config in settings.TASKS.items()
                    if settings.REACTION_FAMILY in config['families'] and not config['purchasable']
                ],
                "color": settings.ACTIVITY_COLORS[settings.REACTION_FAMILY],
            },
            {
                "title": _("MEMORY"),
                "icon": "atlas://data/atlas/menu/memory",
                "tasks": [
                    key for key, config in settings.TASKS.items()
                    if settings.MEMORY_FAMILY in config['families']
                ],
                "color": settings.ACTIVITY_COLORS[settings.MEMORY_FAMILY],
            },
            {
                "title": _("ANALYTICS PREMIUM"),
                "icon": "atlas://data/atlas/menu/analytics",
                "tasks": [
                    key for key, config in settings.TASKS.items()
                    if settings.ANALYTICS_FAMILY in config['families']
                ],
                "color": settings.ACTIVITY_COLORS[settings.ANALYTICS_FAMILY],
                "purchases_needed": ['lifetime_premium', 'premium_subscription'] if settings.INAPP_PURCHASES else []
            },
            {
                "title": _("ATTENTION PREMIUM"),
                "icon": "atlas://data/atlas/menu/attention",
                "tasks": [
                    key for key, config in settings.TASKS.items()
                    if settings.ATTENTION_FAMILY in config['families']
                ],
                "color": settings.ACTIVITY_COLORS[settings.ATTENTION_FAMILY],
                "purchases_needed": ['lifetime_premium', 'premium_subscription'] if settings.INAPP_PURCHASES else []
            },
            {
                "title": _("MATH GEEK SET"),
                "icon": "atlas://data/atlas/purchases/calculation_arena",
                "tasks": ["division_calculation", "percents_calculation", "multiplication_calculation"],
                "color": settings.ACTIVITY_COLORS[None],
                "purchases_needed": ['analytics_arena_pack', 'lifetime_premium',
                                     'premium_subscription'] if settings.INAPP_PURCHASES else []
            },
            {
                "title": _("TIME TASKS SET"),
                "icon": "atlas://data/atlas/purchases/time_arena",
                "tasks": ["time_subtraction", "time_calculation_minutes"],
                "color": settings.ACTIVITY_COLORS[None],
                "purchases_needed": ['time_arena_pack', 'lifetime_premium',
                                     'premium_subscription'] if settings.INAPP_PURCHASES else []
            },
            {
                "title": _("CLASH TASKS SET"),
                "icon": "atlas://data/atlas/purchases/clash_arena",
                "tasks": ["find_figures", "find_primer"],
                "color": settings.ACTIVITY_COLORS[None],
                "purchases_needed": ['clash_arena_pack', 'lifetime_premium',
                                     'premium_subscription'] if settings.INAPP_PURCHASES else []
            }
        ]

    def fill(self, *args):
        self.container.clear_widgets()
        for config in self.get_config():
            task_set = TaskSet(screen=self, **config)
            self.container.add_widget(task_set)
        self.container.height = len(self.container.children) * self.container.children[0].height
