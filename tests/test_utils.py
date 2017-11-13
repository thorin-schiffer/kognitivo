import functools


def override_settings(**settings):
    def real_override_settings(function):
        @functools.wraps(function)
        def inner_override_settings(*args, **kwargs):
            function(*args, **kwargs)

        inner_override_settings.settings = settings
        inner_override_settings.__wrapped__ = function
        return inner_override_settings

    return real_override_settings