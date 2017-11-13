import re

import pytest
from task_widgets.find_in_table import find_number, find_color, find_symbol

from task_widgets.find_in_table import find_letter
from tests import control


@pytest.fixture(params=[
                    find_number.FindNumber,
                    find_letter.FindLetter,
                    find_color.FindColor,
                    find_symbol.FindSymbol,
                ],
                ids=[
                    "find_number",
                    "find_letter",
                    "find_color",
                    "find_symbol",
                ])
def task(request):
    return request.param()


def test_find_in_table_basic(running_app, task):
    task.start()
    assert len(
        [button for button in task.answer_widget.buttons if button.text == unicode(task.correct_answer)]
    ) == task.SIZE

    for button in task.get_correct_answer_widgets():
        assert not task.successful
        control.press(button)

    assert task.successful


def test_find_primer(running_app):
    from task_widgets.find_in_table.find_primer import FindPrimer
    task = FindPrimer()
    task.start()

    count_correct = 0
    for button in task.answer_widget.buttons:
        text = button.text
        print text
        left, right = text.split("=")
        if "+" in left:
            first, second = left.split("+")
            if int(first) + int(second) == int(right):
                count_correct += 1
        else:
            first, second = left.split("-")
            if int(first) - int(second) == int(right):
                count_correct += 1
    assert count_correct == task.SIZE

    for button in task.get_correct_answer_widgets():
        assert not task.successful
        control.press(button)

    assert task.successful


def test_find_figures(running_app):
    from task_widgets.find_in_table.find_figures import FindFigures
    task = FindFigures()
    task.start()

    assert len(
        [button for button in task.answer_widget.buttons if task.FIGURES[button.text] == button.icon_src]
    ) == task.SIZE

    for button in task.get_correct_answer_widgets():
        assert not task.successful
        control.press(button)

    assert task.successful


def test_find_contraversal(running_app):
    from task_widgets.find_in_table.find_contraveral import FindContraversal
    task = FindContraversal()
    task.start()

    correct_count = 0
    for button in task.answer_widget.buttons:
        # text sample [color=#000000FF]GREEN[/color]
        match = re.match(r'\[color=(.*?)\](.*?)\[/color\]', button.text)
        assert match
        color_hex, color_name = match.groups()
        if task.COLORS[color_name] == color_hex:
            correct_count += 1
    assert correct_count == task.SIZE

    for button in task.get_correct_answer_widgets():
        assert not task.successful
        control.press(button)

    assert task.successful
