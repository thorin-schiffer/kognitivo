from collections import OrderedDict

import pytest

from tests import control, assertions
from tests.test_utils import override_settings


@pytest.fixture
def screen(running_app, root_manager):
    from screens.tasks.tasks import TasksScreen

    s = TasksScreen()
    root_manager.add_widget(s)
    return s


def test_enter_tasks(root_manager, screen, tracker, storage):
    control.enter(screen)
    assert not root_manager.has_screen('menu')
    assert not root_manager.has_screen('activity')
    assert not root_manager.has_screen('purchases')
    assert screen._main_manager is not None
    from library_widgets import LoadingWidget

    assert not any(isinstance(child, LoadingWidget) for child in screen.children)

    assertions.assert_tracker_event_sent(tracker, 'tasks', 'sessions', label='started', value=1)
    assert storage['sessions']['started'] == 1


def test_addicted_achievement(screen, google_client):
    for i in range(10):
        control.enter(screen)
    assert screen.played_times == 10
    assertions.assert_achievement_unlocked(google_client, 'addicted')


def test_leave_tasks(screen, mocker):
    control.enter(screen)
    control.leave(screen)


def test_re_enter(screen, mocker):
    control.enter(screen)
    screen.main_manager.current = 'outro'
    control.leave(screen)
    control.enter(screen)
    assert screen.main_manager.current == 'task_sets'


def test_manager_build(running_app, billing, mocker):
    from screens.tasks.content import TaskScreenManager

    manager = TaskScreenManager()
    assert manager.outro is not None
    assert manager.test_screen is not None

    mocker.spy(manager.test_screen, 'start_test')
    manager.start_test()
    manager.test_screen.start_test.assert_called_with(None, None)
    manager.test_screen.current_task.start()
    manager.test_screen.current_task.finish()

    manager.test_screen.to_test_outro()

    assert manager.current == 'outro'
    assert manager.points == manager.test_screen.points == manager.outro.points
    assert manager.day_efficiency == manager.test_screen.day_efficiency == manager.outro.day_efficiency
    assert manager.week_efficiency == manager.test_screen.week_efficiency == manager.outro.week_efficiency


@pytest.fixture
def test_screen(billing):
    from screens.tasks.content import TestScreen
    return TestScreen()


@pytest.fixture
def test_screen_no_billing(billing_no_connection):
    from screens.tasks.content import TestScreen
    return TestScreen()


def test_test_screen_build(test_screen):
    test_screen.start_test()


def test_test_screen_build(test_screen):
    import settings
    test_screen.start_test(family=settings.ATTENTION_FAMILY)


def test_test_screen_get_classes_free(test_screen_no_billing):
    import settings

    free_classes = {key: config for key, config in settings.TASKS.items() if not config['purchasable']}

    classes = test_screen_no_billing.get_task_classes()
    assert set(classes) == set([key for key, config in free_classes.items()])

    for family in [settings.ANALYTICS_FAMILY, settings.REACTION_FAMILY,
                   settings.ATTENTION_FAMILY, settings.MEMORY_FAMILY]:
        classes = test_screen_no_billing.get_task_classes(family=family)
        assert set(classes) == set(
            [key for key, config in free_classes.items() if family in config['families']]
        )


@override_settings(
    INAPP_PURCHASES=OrderedDict([
        ("test_purchase", {
            "icon": "atlas://data/atlas/purchases/lifetime_premium",
            "unlocks_tasks": ["find_figures", "find_primer"],
            "type": "inapp"
        })])
)
def test_test_screen_get_classes_purchased(test_screen, billing):
    import settings
    billing.buy("test_purchase")
    free_classes = {key: config for key, config in settings.TASKS.items() if not config['purchasable']}

    classes = test_screen.get_task_classes()
    assert set(classes) == set([key for key, config in free_classes.items()] + ["find_figures", "find_primer"])

    classes = test_screen.get_task_classes(family=settings.ATTENTION_FAMILY)
    assert set(classes) == set(
        [key for key, config in free_classes.items() if settings.ATTENTION_FAMILY in config['families']] +
        ["find_figures", "find_primer"]
    )

    classes = test_screen.get_task_classes(family=settings.MEMORY_FAMILY)
    assert set(classes) == set(
        [key for key, config in free_classes.items() if settings.MEMORY_FAMILY in config['families']]
    )


@override_settings(
    INAPP_PURCHASES=OrderedDict([
        ("test_purchase", {
            "icon": "atlas://data/atlas/purchases/lifetime_premium",
            "unlocks_tasks": None,
            "type": "inapp"
        })])
)
def test_test_screen_get_classes_premium(test_screen, billing):
    import settings
    billing.buy("test_purchase")

    classes = test_screen.get_task_classes()
    assert set(classes) == set([key for key, config in settings.TASKS.items()] + ["find_figures", "find_primer"])

    for family in [settings.ANALYTICS_FAMILY, settings.REACTION_FAMILY,
                   settings.ATTENTION_FAMILY, settings.MEMORY_FAMILY]:
        classes = test_screen.get_task_classes(family=family)
        assert set(classes) == set(
            [key for key, config in settings.TASKS.items() if family in config['families']]
        )


def test_task_icon():
    from screens.tasks.content import TaskIcon

    icon = TaskIcon()
    assert not icon.is_complete
    icon.task_class = "numbers_calculation"
    assert icon.incomplete_source == "atlas://data/atlas/tasks/numbers_calculation"
    assert icon.source == icon.incomplete_source
    icon.is_complete = True
    assert icon.source == icon.complete_source
    icon.is_complete = False
    assert icon.source == icon.incomplete_source


def test_task_status(storage):
    from screens.tasks.content import TestStatus
    from utils import _

    status = TestStatus()
    status.task_number = 1
    assert status.task_number_widget.text == _(u"[color=#408742ff][font=glyphicons]\uE006[/font][/color] task #1/4")

    storage["task_records"]["numbers_calculation"] = 100
    status.task = "numbers_calculation"
    assert status.best_points_widget.text == "BEST RESULT: [b]100[/b] POINTS"


def test_test_screen_task_finished(test_screen):
    test_screen.start_test(tasks=['numbers_calculation', 'find_color'])
    test_screen.current_task.start()
    test_screen.current_task.finish()
    assert test_screen.points == test_screen.current_task.points
    assert test_screen.icon.is_complete
    assert test_screen.day_efficiency
    assert test_screen.week_efficiency
    assert test_screen.points
    test_screen.load_next_task()
    assert not test_screen.icon.is_complete


def test_screen_to_outro(test_screen, tracker, google_client):
    from settings import LEADERBOARD
    test_screen.to_test_outro()
    assertions.assert_tracker_event_sent(tracker, 'tasks', 'sessions', label='finished', value=1)
    assertions.assert_leaderboard_score_submitted(google_client, LEADERBOARD, test_screen.points)


def test_test_outro(running_app, ):
    from screens.tasks.content import TestOutro
    outro = TestOutro()
    outro.day_efficiency = 1.0
    assert outro.day_diagram.part == outro.day_efficiency

    outro.week_efficiency = 1.1
    assert outro.week_diagram.part == outro.week_efficiency

    outro.points = 100
    assert outro.status_label.text == "PERFECT\n[size=20sp][color=#6666660A]100 POINTS[/color][/size]"
    assert outro.status_image.source == "data/img/status_icons/icon_100.png"
