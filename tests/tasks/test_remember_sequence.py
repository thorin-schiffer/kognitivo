import pytest
from task_widgets.remember_sequence import number_sequence, symbol_sequence, color_sequence

from task_widgets.remember_sequence import letter_sequence
from tests import control, assertions


@pytest.fixture(params=[
    number_sequence.NumberSequence,
    letter_sequence.LetterSequence,
    symbol_sequence.SymbolSequence,
    color_sequence.ColorSequence
],
    ids=[
        "number_sequence",
        "letter_sequence",
        "symbol_sequence",
        "color_sequence"
    ])
def task(request):
    return request.param()


def test_remember_sequence(running_app, task, vibrator):
    task.start()
    task.on_timeout()
    assert task.answer_widget

    incorrect_button = task.get_incorrect_answer_widgets()[0]
    control.press(incorrect_button)
    assertions.assert_vibrated(vibrator, 100)

    for i in range(task.SIZE):
        assert not task.successful
        button = task.get_correct_answer_widgets()[0]
        assert button.text == unicode(task.correct_answer)
        control.press(button)

    assert task.successful
