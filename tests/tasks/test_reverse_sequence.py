import pytest

from task_widgets.reverse_sequence import reverse_numbers, reverse_letters
from tests import control


@pytest.fixture(params=[
                    reverse_numbers.ReverseNumbers,
                    reverse_letters.ReverseLetters,
                ],
                ids=[
                    "number_sequence",
                    "letter_sequence",
                ])
def task(request):
    return request.param()


def test_reverse_sequence(running_app, task):
    task.start()
    assert any(
        button.text == "[color=#ccccccff]|[/color]".join(task.correct_answer)
        for button in task.answer_widget.buttons
    )
    correct_button = task.get_correct_answer_widgets()[0]
    control.press(correct_button)
    assert task.successful


def test_reverse_symbols_sequence(running_app):
    from task_widgets.reverse_sequence.reverse_symbols import ReverseSymbols
    task = ReverseSymbols()
    task.start()
    assert any(
        button.text == u"[color=#ccccccff][font=RobotoCondensed]|[/font][/color]".join(task.correct_answer)
        for button in task.answer_widget.buttons
    )
    correct_button = task.get_correct_answer_widgets()[0]
    control.press(correct_button)
    assert task.successful
