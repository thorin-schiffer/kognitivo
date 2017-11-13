from control import press


def test_tutorial_screen(running_app, root_manager):
    from screens.tutorial import TutorialScreen
    screen = TutorialScreen()
    manager = screen.main_manager
    assert manager.current == 'welcome'
    assert manager.has_screen('start_test')
    assert manager.has_screen('tasks_to_stats')
    assert manager.has_screen('categories')
    assert manager.has_screen('notifications')
    assert manager.has_screen('tasks')
    assert manager.has_screen('results')
    start_test_screen = manager.get_screen('start_test')
    press(start_test_screen.next_button)
    assert root_manager.current == 'tasks'


def test_tutorial_mixin(running_app):
    from screens.activity.content import FilterPanel
    panel = FilterPanel()
    panel.show_tutorial()
    assert panel._top_rectangle
    assert panel._bottom_rectangle
    assert panel._left_rectangle
    assert panel._right_rectangle
    panel.hide_tutorial()


def test_tutorial_mixin_chain(running_app):
    from screens.activity.content import FilterPanel
    panel1 = FilterPanel()
    panel2 = FilterPanel()
    panel1.show_tutorial(next_widgets=[panel2])
    panel1.hide_tutorial()
