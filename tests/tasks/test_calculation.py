# coding=utf-8
from datetime import datetime, timedelta

import pytest

from tests import control
from utils import _


@pytest.mark.parametrize("mode", [
    0, 1, 2
], ids=['mode0', 'mode1', 'mode2'])
def test_numbers_calculation(running_app, mode):
    from task_widgets.calculation.numbers_calculation import NumbersCalculation

    task = NumbersCalculation(mode=mode)

    assert task.intro_hint.title == _("Super Brain")
    assert task.intro_hint.description == _("Calculate the result!")
    task.start()
    if mode == 0:
        assert task.description_widget.text == "%s + %s = ?" % (task.first, task.second)
        assert task.correct_answer == task.first + task.second
    elif mode == 1:
        assert task.description_widget.text == "? + %s = %s" % (task.second, task.result)
        assert task.correct_answer == task.result - task.second
    elif mode == 2:
        assert task.description_widget.text == "%s + ? = %s" % (task.first, task.result)
        assert task.correct_answer == task.result - task.first

    assert any(button.text == unicode(task.correct_answer) for button in task.answer_widget.buttons)

    correct_button = task.get_correct_answer_widgets()[0]
    control.press(correct_button)
    assert task.successful


@pytest.mark.parametrize("mode", [
    0, 1, 2
], ids=['mode0', 'mode1', 'mode2'])
def test_division(running_app, mode):
    from task_widgets.calculation.division import DivisionCalculation

    task = DivisionCalculation(mode=mode)
    assert task.intro_hint.title == _("Super Brain: Division")
    assert task.intro_hint.description == _("Calculate the result!")
    task.start()
    if mode == 0:
        assert task.description_widget.text == u"%s ÷ %s = ?" % (task.first, task.second)
        assert task.correct_answer == task.first / task.second
    elif mode == 1:
        assert task.description_widget.text == u"? ÷ %s = %s" % (task.second, task.result)
        assert task.correct_answer == task.result * task.second
    elif mode == 2:
        assert task.description_widget.text == u"%s ÷ ? = %s" % (task.first, task.result)
        assert task.correct_answer == task.first / task.result

    assert any(button.text == unicode(task.correct_answer) for button in task.answer_widget.buttons)

    correct_button = task.get_correct_answer_widgets()[0]
    control.press(correct_button)
    assert task.successful


@pytest.mark.parametrize("mode", [
    0, 1, 2
], ids=['mode0', 'mode1', 'mode2'])
def test_multiplication(running_app, mode):
    from task_widgets.calculation.multiplication import MultiplicationCalculation

    task = MultiplicationCalculation(mode=mode)
    assert task.intro_hint.title == _("Multi Super Brain")
    assert task.intro_hint.description == _("Calculate the result!")
    task.start()
    if mode == 0:
        assert task.description_widget.text == u"%s × %s = ?" % (task.first, task.second)
        assert task.correct_answer == task.first * task.second
    elif mode == 1:
        assert task.description_widget.text == u"? × %s = %s" % (task.second, task.result)
        assert task.correct_answer == task.result / task.second
    elif mode == 2:
        assert task.description_widget.text == u"%s × ? = %s" % (task.first, task.result)
        assert task.correct_answer == task.result / task.first

    assert any(button.text == unicode(task.correct_answer) for button in task.answer_widget.buttons)

    correct_button = task.get_correct_answer_widgets()[0]
    control.press(correct_button)
    assert task.successful


def test_percents(running_app):
    from task_widgets.calculation.percents import PercentsCalculation

    task = PercentsCalculation()
    assert task.intro_hint.title == _("Super Brain: Percents")
    assert task.intro_hint.description == _("Calculate the result!")
    task.start()

    assert task.description_widget.text == _(u"%(percents)s%% of %(base)s?") % {
        "percents": task.second,
        "base": task.first
    }
    assert task.correct_answer == (task.first * task.second) / 100.

    assert any(button.text == task.variant_modifier(task.correct_answer) for button in task.answer_widget.buttons)

    correct_button = task.get_correct_answer_widgets()[0]
    control.press(correct_button)
    assert task.successful


def test_time_calculation_normal(running_app):
    from task_widgets.calculation.time_calculation import TimeCalculation

    first = datetime(2000, 1, 1, hour=1, minute=30)
    second = timedelta(hours=1, minutes=30)

    task = TimeCalculation(first=first, second=second)
    assert task.intro_hint.title == _("Time Machine")
    assert task.intro_hint.description == _("Add the interval of the\n right clock to the left one")
    task.start()

    assert task.correct_answer == task.result == task.first + task.second

    assert task.description_widget.left_clock.hour == first.hour
    assert task.description_widget.left_clock.minute == first.minute

    assert task.description_widget.left_clock.hour_angle == -45.0
    assert task.description_widget.left_clock.minute_angle == -180.0

    assert task.description_widget.right_clock.hour == 1
    assert task.description_widget.right_clock.minute == 30

    assert task.description_widget.left_clock.hour_angle == -45.0

    assert any(button.text == task.variant_modifier(task.correct_answer) for button in task.answer_widget.buttons)

    correct_button = task.get_correct_answer_widgets()[0]
    control.press(correct_button)
    assert task.successful


def test_time_calculation_substraction(running_app):
    from task_widgets.calculation.time_subtraction import TimeSubtraction

    first = datetime(2000, 1, 1, hour=1, minute=30)
    second = timedelta(hours=1, minutes=30)

    task = TimeSubtraction(first=first, second=second)
    assert task.intro_hint.title == _("Time Machine: Subtraction")
    assert task.intro_hint.description == _("Subtract the interval of the\n right clock to the left one")
    task.start()

    assert task.correct_answer == task.result == task.first - task.second

    assert task.description_widget.left_clock.hour == first.hour
    assert task.description_widget.left_clock.minute == first.minute

    assert task.description_widget.right_clock.hour == 1
    assert task.description_widget.right_clock.minute == 30

    assert any(button.text == task.variant_modifier(task.correct_answer) for button in task.answer_widget.buttons)

    correct_button = task.get_correct_answer_widgets()[0]
    control.press(correct_button)
    assert task.successful


def test_time_calculation_minutes(running_app):
    from task_widgets.calculation.time_calculation_minutes import TimeCalculationMinutes

    first = datetime(2000, 1, 1, hour=1, minute=30)
    second = timedelta(hours=1, minutes=30)

    task = TimeCalculationMinutes(first=first, second=second)
    assert task.intro_hint.title == _("Time Machine: Last Minutes")
    assert task.intro_hint.description == _("Add the interval in minutes of the\n right clock to the left one")
    task.start()

    assert task.correct_answer == task.result == task.first + task.second

    assert task.description_widget.left_clock.hour == first.hour
    assert task.description_widget.left_clock.minute == first.minute

    assert task.description_widget.right_clock.hour == 1
    assert task.description_widget.right_clock.minute == 30

    assert any(button.text == task.variant_modifier(task.correct_answer) for button in task.answer_widget.buttons)

    correct_button = task.get_correct_answer_widgets()[0]
    control.press(correct_button)
    assert task.successful
