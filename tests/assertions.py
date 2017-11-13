def assert_modal_view_shown(running_app, klass=None):
    assert running_app.root_window.children
    if klass:
        klass_found = False
        children = running_app.root_window.children
        for child in children:
            klass_found |= isinstance(child, klass)
        assert klass_found, "%s modal view not found in %s" % (klass, children)


def assert_modal_view_not_shown(running_app, klass=None):
    if not klass:
        assert not running_app.root_window.children
    else:
        klass_found = False
        children = running_app.root_window.children
        for child in children:
            klass_found |= isinstance(child, klass)
        assert not klass_found, "%s modal view found in %s" % (klass, children)


def assert_tracker_event_sent(tracker, category, action, *args, **kwargs):
    tracker.send_event.assert_called_with(category, action, *args, **kwargs)


def assert_bought(billing, sku, *args, **kwargs):
    billing.buy.assert_any_call(sku, *args, **kwargs)


def assert_achievement_incremented(google_client, name):
    google_client.increment_achievement.assert_any_call(name)


def assert_achievement_unlocked(google_client, name):
    google_client.unlock_achievement.assert_any_call(name)


def assert_leaderboard_score_submitted(google_client, name, score):
    google_client.submit_score.assert_any_call(name, score)


def assert_vibrated(vibrator, length):
    vibrator.vibrate.assert_any_call(length)
