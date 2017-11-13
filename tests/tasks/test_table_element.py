import pytest
from task_widgets.table_element import number_table, letter_table, symbol_table

from task_widgets.table_element import color_table
from tests import control


@pytest.fixture(params=[
                    number_table.NumberTable,
                    letter_table.LetterTable,
                    symbol_table.SymbolTable,
                    color_table.ColorTable
                ],
                ids=[
                    "number_table",
                    "letter_table",
                    "symbol_table",
                    "color_table"
                ])
def task(request):
    return request.param()


def test_table_element(running_app, task):
    task.start()
    task.on_timeout()
    assert task.answer_widget
    assert any(
        button.text == task.correct_answer
        for button in task.answer_widget.buttons
    )

    correct_button = task.get_correct_answer_widgets()[0]
    control.press(correct_button)
    assert task.successful
