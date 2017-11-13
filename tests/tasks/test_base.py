# coding=utf-8
import pytest

from tests import assertions
from tests import control


@pytest.fixture
def task(running_app, monkeypatch):
    from task_widgets.calculation.numbers_calculation import NumbersCalculation

    return NumbersCalculation(
        first=1,
        second=2,
        mode=0
    )


def test_base_build(task):
    assert task.answer_widget is None
    assert task.description_widget is None
    task.show_intro_hint()
    task.start()
    assert task.answer_widget
    assert task.description_widget
    assert task.intro_hint is None


def test_base_answer(task, tracker, google_client, mocker, vibrator):
    from managers.database import database_manager
    mocker.spy(database_manager, 'add_stat')
    from task_widgets.calculation.numbers_calculation import NumbersCalculation
    task = NumbersCalculation()
    task.start()

    correct_button = task.get_correct_answer_widgets()
    incorrect_button = [button for button in task.answer_widget.buttons if button not in correct_button][0]
    control.press(incorrect_button)
    assert task.mistakes_count == 1
    assertions.assert_vibrated(vibrator, 100)
    correct_button = correct_button[0]
    control.press(correct_button)
    assert task.successful
    assertions.assert_tracker_event_sent(tracker, 'tasks', 'class', label="numbers_calculation")
    assertions.assert_achievement_incremented(google_client, "general_cognitive")
    assertions.assert_achievement_incremented(google_client, "sergeant_cognitive")
    assertions.assert_achievement_incremented(google_client, "major_cognitive")
    assertions.assert_achievement_incremented(google_client, "lieutenant_cognitive")
    assertions.assert_achievement_incremented(google_client, "colonel_cognitive")

    assert database_manager.add_stat.called


def test_status_bar(running_app):
    from task_widgets.task_base.status_bar import TaskStatusBar
    status_bar = TaskStatusBar()
    assert status_bar.correctness_widget
    assert status_bar.points_widget
    status_bar.mistakes_count = 1
    assert status_bar.correctness_widget.text == u"[color=#408742ff][font=glyphicons][/font]0[/color]  " \
                                                 u"[color=#eb542cff][font=glyphicons][/font]1[/color]"
    status_bar.correct_count = 1
    assert status_bar.correctness_widget.text == u"[color=#408742ff][font=glyphicons][/font]1[/color]  " \
                                                 u"[color=#eb542cff][font=glyphicons][/font]1[/color]"
    status_bar.points = 100
    assert status_bar.points_widget.text == u"100\n[size=10]POINTS[/font]"
    status_bar.time = 10
    assert status_bar.time_widget.label.text == u"[b]10.0[/b] [size=16]sec[/size]"
