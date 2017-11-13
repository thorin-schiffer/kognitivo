def enter(screen):
    screen.dispatch('on_pre_enter')
    screen.dispatch('on_enter')


def leave(screen):
    screen.dispatch('on_pre_leave')
    screen.dispatch('on_leave')


def press(button):
    button.dispatch('on_press')


def release(button):
    button.dispatch('on_release')


def get_popups(running_app):
    return running_app.root_window.children
