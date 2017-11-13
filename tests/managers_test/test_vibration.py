def test_respect_settings(running_app, vibrator):
    config = running_app.config
    config.set('preferences', 'vibration', 0)
    assert not vibrator.turned_on()
