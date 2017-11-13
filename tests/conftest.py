import sys
import os
from datetime import timedelta, datetime

from kivy.core.audio import Sound
from kivy.core.window import window_sdl2  # noqa
import pytest


def start(animation, widget):
    animation.dispatch('on_start', widget)

    for proprety_name, value in animation.animated_properties.items():
        setattr(widget, proprety_name, value)
    animation.dispatch('on_complete', widget)


@staticmethod
def load(name):
    return Sound()


@pytest.fixture(autouse=True)
def patch_env(request, monkeypatch):
    test_name = request._pyfuncitem.name
    try:
        import settings

        reload(settings)
        from configure import configure
        settings.KIVY_GRAPHICS_WIDTH = 1
        settings.KIVY_GRAPHICS_HEIGHT = 1
        configure()
        settings.DATABASE_NAME = "test-%s-db.sqlite3" % test_name
        settings.DATABASE_PATH = os.path.join(settings.PROJECT_DIR, settings.DATABASE_NAME)

        # try to import module overriding
        module_overrides = getattr(request.module, "SETTINGS_OVERRIDE", {})
        for option_name, option_value in module_overrides.items():
            setattr(settings, option_name, option_value)

        from kivy.config import ConfigParser
        ConfigParser._named_configs = {}

        # apply overriding from the function itself
        if hasattr(request.function, 'settings'):
            function_overrides = request.function.settings
            for option_name, option_value in function_overrides.items():
                setattr(settings, option_name, option_value)
            sys.modules["settings"] = settings

        monkeypatch.setattr('kivy.animation.Animation.start', start)
        monkeypatch.setattr('kivy.clock.Clock.create_trigger', lambda c, t=None: c)
        monkeypatch.setattr('kivy.core.audio.SoundLoader.load', load)

        def fin():
            from managers.database import database_manager

            if database_manager._connection:
                database_manager._connection.close()
                database_manager._connection = None
            if os.path.exists("test-%s-db.sqlite3" % test_name):
                os.remove("test-%s-db.sqlite3" % test_name)

            if os.path.exists("kognitivo-test-%s.ini" % test_name):
                os.remove("kognitivo-test-%s.ini" % test_name)

        request.addfinalizer(fin)
    except:
        if os.path.exists("test-%s-db.sqlite3" % test_name):
            os.remove("test-%s-db.sqlite3" % test_name)

        if os.path.exists("kognitivo-test-%s.ini" % test_name):
            os.remove("kognitivo-test-%s.ini" % test_name)
        raise


@pytest.fixture(params=[
    "en", "es", "ru", "de", "ua"
], ids=[
    "en_lang", "es_lang", "ru_lang", "de_lang", "ua_lang"
])
def app(request):
    from main import KognitivoApp

    test_name = request._pyfuncitem.name
    application = KognitivoApp(name="kognitivo-test-%s" % test_name)
    application.lang = request.param
    from utils import _
    _.switch_lang(application.lang)

    def fin():
        if os.path.exists(application.storage.filename):
            os.remove(application.storage.filename)

    request.addfinalizer(fin)
    return application


@pytest.fixture
def running_app(monkeypatch, app):
    @staticmethod
    def get_running_app(**kwargs):
        if not app.manager:
            from root_manager import RootManager

            app.manager = RootManager()
            from kivy.base import EventLoop

            window = EventLoop.window
            app._app_window = window
            window.children = []

        if not app.config:
            app.load_config()
        return app

    monkeypatch.setattr('kivy.base.runTouchApp', lambda: None)

    monkeypatch.setattr('kivy.app.App.get_running_app', get_running_app)
    from kivy.app import App

    return App.get_running_app()


@pytest.fixture
def root_manager(running_app):
    return running_app.manager


@pytest.fixture
def navigation(running_app):
    return running_app.root


@pytest.fixture
def empty_data(monkeypatch):
    monkeypatch.setattr('managers.database.database_manager.day_percents', lambda *args, **kwargs: {})
    monkeypatch.setattr('managers.database.database_manager.hour_percents', lambda *args, **kwargs: {})
    monkeypatch.setattr('managers.database.database_manager.recent_percents', lambda *args, **kwargs: {})


@pytest.fixture
def not_empty_data(monkeypatch):
    monkeypatch.setattr('managers.database.database_manager.hour_percents',
                        lambda *args, **kwargs: {key: 1.0 for key in range(24)})
    monkeypatch.setattr('managers.database.database_manager.day_percents',
                        lambda *args, **kwargs: {key: 1.0 for key in range(7)})
    monkeypatch.setattr('managers.database.database_manager.recent_percents',
                        lambda *args, **kwargs: {(datetime.now() - timedelta(days=key)).date(): 1.0 for key in
                                                 range(7)})


@pytest.fixture
def webbrowser(mocker):
    mock_webbrowser_open = mocker.patch('webbrowser.open')
    return mock_webbrowser_open


@pytest.fixture
def tracker(mocker, running_app):
    mocker.spy(running_app.tracker, 'send_event')
    return running_app.tracker


@pytest.fixture
def google_client(mocker, running_app):
    mocker.spy(running_app.google_client, 'increment_achievement')
    mocker.spy(running_app.google_client, 'unlock_achievement')
    mocker.spy(running_app.google_client, 'submit_score')
    return running_app.google_client


@pytest.fixture
def vibrator(mocker):
    from managers.vibration import vibration_manager
    mocker.spy(vibration_manager, 'vibrate')
    return vibration_manager


@pytest.fixture
def storage(running_app):
    return running_app.storage


@pytest.fixture
def billing(running_app, mocker):
    running_app.initialize_billing()
    mocker.spy(running_app.billing, 'buy')
    return running_app.billing


@pytest.fixture
def billing_no_connection(running_app, monkeypatch):
    running_app.initialize_billing()
    monkeypatch.setattr('billing.BillingService.get_available_items', lambda *args, **kwargs: [])
    return running_app.billing
