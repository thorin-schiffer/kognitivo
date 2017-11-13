from kivy.utils import get_hex_from_color

import pytest
from task_widgets.find_in_table_dynamic import find_letter_dynamic, find_symbol_dynamic

from task_widgets.find_in_table_dynamic import find_number_dynamic
from tests import control, assertions


@pytest.fixture(params=[
                    find_number_dynamic.FindNumberDynamic,
                    find_letter_dynamic.FindLetterDynamic,
                    find_symbol_dynamic.FindSymbolDynamic,
                ],
                ids=[
                    "find_number_dynamic",
                    "find_letter_dynamic",
                    "find_symbol_dynamic",
                ])
def task(request):
    return request.param()


def test_find_in_table_dynamic(running_app, task, vibrator):
    task.start()
    assert len(
        [button for button in task.answer_widget.buttons if button.text == unicode(task.correct_answer)]
    ) == task.SIZE

    incorrect_button = task.get_incorrect_answer_widgets()[0]
    control.press(incorrect_button)
    assertions.assert_vibrated(vibrator, 100)

    for button in task.get_correct_answer_widgets():
        assert not task.successful
        control.press(button)

    assert task.successful


def test_find_color_dynamic(running_app):
    from task_widgets.find_in_table_dynamic.find_color_dynamic import FindColorDynamic
    task = FindColorDynamic()
    task.start()
    assert len(
        [button for button in task.answer_widget.buttons
         if get_hex_from_color(button.inner_color) == unicode(task.correct_answer)]
    ) == task.SIZE

    for button in task.get_correct_answer_widgets():
        assert not task.successful
        control.press(button)

    assert task.successful
