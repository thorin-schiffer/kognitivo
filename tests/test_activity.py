import pytest

import control
from tests import assertions


@pytest.fixture
def screen(running_app, root_manager):
    from screens.activity.activity import ActivityScreen

    s = ActivityScreen()
    root_manager.add_widget(s)
    return s


def test_enter_activity(not_empty_data, root_manager, screen):
    control.enter(screen)
    assert not root_manager.has_screen('menu')
    assert not root_manager.has_screen('tasks')
    assert not root_manager.has_screen('purchases')
    assert screen._panel is not None

    from library_widgets import LoadingWidget

    assert not any(isinstance(child, LoadingWidget) for child in screen.children)


def test_filter_panel(not_empty_data, root_manager, screen):
    filter_panel = screen.panel.filter_panel
    assert root_manager.get_screen('activity') is screen
    for button in filter_panel.buttons:
        control.press(button)
        filter_panel.family = button.family
        assert screen.family == button.family
        assert screen.panel.tab_panel.current_tab.family == button.family
        for tab in screen.panel.tab_panel.tab_list:
            assert tab.family == button.family


def test_filter_panel_select_button(not_empty_data, root_manager, screen):
    filter_panel = screen.panel.filter_panel
    assert root_manager.get_screen('activity') is screen
    control.enter(screen)
    screen.check_tutorial()
    assert screen.family is None


def test_tabs(not_empty_data, root_manager, screen):
    panel = screen.panel
    control.press(panel.day_tab)
    control.release(panel.day_tab)
    assert panel.tab_panel.current_tab == panel.day_tab

    control.press(panel.week_tab)
    control.release(panel.week_tab)
    assert panel.tab_panel.current_tab == panel.week_tab

    control.press(panel.progress_tab)
    control.release(panel.progress_tab)
    assert panel.tab_panel.current_tab == panel.progress_tab


def test_rate_popup(monkeypatch, not_empty_data, root_manager, screen, running_app):
    monkeypatch.setattr('screens.activity.activity.ActivityScreen._to_show_rate_popup', lambda *args: True)
    control.enter(screen)
    from screens.activity.content import RatePopup
    control.enter(screen)
    assertions.assert_modal_view_shown(running_app, RatePopup)


def test_like_popup(monkeypatch, not_empty_data, root_manager, screen, running_app):
    monkeypatch.setattr('screens.activity.activity.ActivityScreen._to_show_rate_popup', lambda *args: False)
    monkeypatch.setattr('screens.activity.activity.ActivityScreen._to_show_like_popup', lambda *args: True)
    control.enter(screen)
    control.enter(screen)
    from screens.activity.content import LikePopup
    assertions.assert_modal_view_shown(running_app, LikePopup)


def test_only_one_popup(monkeypatch, not_empty_data, root_manager, screen, running_app):
    monkeypatch.setattr('screens.activity.activity.ActivityScreen._to_show_like_popup', lambda *args: True)
    monkeypatch.setattr('screens.activity.activity.ActivityScreen._to_show_rate_popup', lambda *args: True)
    control.enter(screen)
    control.enter(screen)
    from screens.activity.content import RatePopup, LikePopup

    assertions.assert_modal_view_shown(running_app, RatePopup)
    assertions.assert_modal_view_not_shown(running_app, LikePopup)


def test_store_feedback_rate_popup(mocker, not_empty_data, tracker):
    from screens.activity.content import RatePopup

    popup = RatePopup()
    popup.store_feedback(True)
    assertions.assert_tracker_event_sent(tracker, 'clicks', 'rate_popup', 'accepted')

    popup.store_feedback(False)
    assertions.assert_tracker_event_sent(tracker, 'clicks', 'rate_popup', 'rejected')


def test_store_feedback_like_popup(not_empty_data, tracker):
    from screens.activity.content import LikePopup

    popup = LikePopup()
    popup.store_feedback(True)
    assertions.assert_tracker_event_sent(tracker, 'clicks', 'fb_like_popup', 'accepted')

    popup.store_feedback(False)
    assertions.assert_tracker_event_sent(tracker, 'clicks', 'fb_like_popup', 'rejected')


def test_faithful_comrade_achievement(not_empty_data, google_client, screen, storage, running_app):
    control.enter(screen)
    storage['starts'] = {"count": 5}
    control.leave(screen)
    assertions.assert_achievement_unlocked(google_client, 'faithful_comrade')
