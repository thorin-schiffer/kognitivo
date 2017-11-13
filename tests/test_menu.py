import pytest

import control
import settings
from tests import assertions
from tests.markers import inapp_purchase


@pytest.fixture
def menu(running_app, root_manager):
    from screens.menu import Menu

    s = Menu()
    return s


def test_press_quick_test(menu, root_manager):
    assert menu.quick_test_button is not None
    control.press(menu.quick_test_button)
    assert not root_manager.has_screen('activity')
    assert root_manager.has_screen('tasks')
    assert not root_manager.has_screen('purchases')
    assert root_manager.current == 'tasks'


def test_press_overview(not_empty_data, menu, root_manager):
    assert menu.overview_button is not None
    control.press(menu.overview_button)
    assert root_manager.has_screen('activity')
    assert not root_manager.has_screen('tasks')
    assert not root_manager.has_screen('purchases')
    assert root_manager.current == 'activity'


def test_press_feedback(empty_data, menu, root_manager, webbrowser):
    assert menu.feedback_button is not None
    control.press(menu.feedback_button)

    webbrowser.assert_called_once_with(settings.FACEBOOK_PAGE_URL)


def test_press_more_apps(empty_data, menu, root_manager, webbrowser):
    assert menu.more_apps_button is not None
    control.press(menu.more_apps_button)

    webbrowser.assert_called_once_with(settings.MORE_APPS_URL)


@inapp_purchase
def test_purchase_button(menu, root_manager):
    assert menu.purchase_button is not None
    control.press(menu.purchase_button)
    assert not root_manager.has_screen('activity')
    assert root_manager.has_screen('purchases')
    assert root_manager.current == 'purchases'


@pytest.mark.skipif(not settings.GOOGLE_PLAY_ACHIEVEMENT_IDS, reason="No achievements, if no achievement ids")
def test_gp_achievements_button(empty_data, menu, root_manager, running_app, mocker):
    assert menu.gp_achievements_button is not None
    show_achievements_mock = mocker.patch('gplay.GoogleClient.show_achievements')
    control.press(menu.gp_achievements_button)
    assert running_app.google_client.is_connected
    assert show_achievements_mock.call_count == 1


@pytest.mark.skipif(not settings.GOOGLE_PLAY_ACHIEVEMENT_IDS, reason="No achievements, if no achievement ids")
def test_gp_achievements_button_connected(empty_data, menu, root_manager, running_app, mocker):
    assert menu.gp_achievements_button is not None
    show_achievements_mock = mocker.patch('gplay.GoogleClient.show_achievements')
    control.press(menu.gp_achievements_button)
    assert running_app.google_client.is_connected
    assert show_achievements_mock.call_count == 1
    control.press(menu.gp_achievements_button)


@pytest.mark.skipif(not settings.LEADERBOARD, reason="No leaderboards")
def test_gp_leaderboard_button(empty_data, menu, root_manager, running_app, mocker):
    assert menu.gp_leaderboard_button is not None
    show_leaderboard_mock = mocker.patch('gplay.GoogleClient.show_leaderboard')
    control.press(menu.gp_leaderboard_button)
    assert running_app.google_client.is_connected
    assert show_leaderboard_mock.call_count == 1


def test_tutorial(menu, root_manager):
    assert menu.help_button is not None
    control.press(menu.help_button)
    assert root_manager.current == 'tutorial'
