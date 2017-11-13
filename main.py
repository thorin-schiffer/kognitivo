def attach_android_context(raven_data):
    from jnius import autoclass

    Build = autoclass("android.os.Build")
    version = autoclass("android.os.Build$VERSION")

    try:
        user_data_dir = app.user_data_dir
    except OSError:
        user_data_dir = None

    raven_data.update({
        "model": Build.MODEL,
        "manufacturer": Build.MANUFACTURER,
        "database_path": settings.DATABASE_PATH,
        "system_version": version.RELEASE,
        "user_dir_path": user_data_dir if app else "APP IS NONE",
    })


def attach_kivy_log(raven_data):
    from kivy.logger import LoggerHistory

    log = [getattr(log_entry, 'message', None) for log_entry in LoggerHistory.history]
    raven_data.update({
        "graceful": True,
        "log": log
    })


# fix for raven, depending on unittest which is in blacklist
app = None
try:
    from app import KognitivoApp

    if __name__ == '__main__':
        app = KognitivoApp()
        app.run()
        app.tracker.send_to_server()
except SystemExit:
    pass
except:  # noqa E722
    # try get more information
    # if exception happens in this block, something really bad happened

    import os
    import sys
    # unittest is not there on android
    import unittest

    sys.modules['unittest'] = unittest

    os.environ['INVOKE'] = "true"
    # settings import should not break anything in non dev
    import settings

    try:
        if not settings.DEVELOPMENT_VERSION:
            from raven import Client

            client = Client(dsn=settings.RAVEN_DSN, list_max_length=1000, string_max_length=10000)
            client.tags_context({
                "version": settings.VERSION
            })
            from kivy.utils import platform

            data = {"graceful": True}
            if platform == 'android':
                attach_android_context(data)
            attach_kivy_log(data)

            client.extra_context(data=data)

            client.tags_context({
                'os': platform,
                'profile': settings.PROFILE
            })
            client.captureException()
        else:
            raise
    except Exception as ex:
        if settings.DEVELOPMENT_VERSION:
            raise
        from raven import Client

        client = Client(dsn=settings.RAVEN_DSN)

        client.extra_context(data={
            "graceful": False,
            "original_exception": unicode(ex)
        })
        client.captureException()
