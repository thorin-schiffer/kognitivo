from tests import control


def test_tip_ball(running_app):

    from task_widgets.tip_ball import TipBall, Ball
    Ball.move_random = lambda *args, **kwargs: None
    task = TipBall()
    task.start()

    for i in range(task.SIZE):
        assert not task.successful
        button = task.get_correct_answer_widgets()[0]
        control.press(button)

    assert task.successful


def test_white_squares(running_app):

    from task_widgets.white_squares import WhiteSquares
    task = WhiteSquares()
    task.start()

    for i in range(task.SIZE):
        assert not task.successful
        task.show_square(None)
        button = task.get_correct_answer_widgets()[0]
        task.hide_square(None)
        control.press(button)

    assert task.successful
