import os
from random import randint, uniform, choice
import runpy

from invoke import task

from datetime import timedelta, datetime
from invoke_collections.utils import tprint
from invoke_collections import kivy_collection


@task
def db(ctx):
    tprint("Filling database with chunks...")
    from managers.database import database_manager
    import settings
    import os
    db_path = os.path.join(settings.PROJECT_DIR, settings.DATABASE_NAME)
    if os.path.exists(db_path):
        os.remove(db_path)

    for i in xrange(14 * 3):
        created = datetime.now() - timedelta(days=randint(0, 13), hours=randint(0, 23))
        database_manager.add_stat(efficiency=uniform(.5, 1.5),
                                  duration=10,
                                  key=choice(settings.TASKS.keys()),
                                  created=created)


@task
def test_raven(ctx):
    import settings
    from raven import Client
    client = Client(settings.RAVEN_DSN)

    try:
        1 / 0
    except ZeroDivisionError:
        client.captureException()


@task
def run(ctx, profile=None):
    profile = profile or ''
    os.environ['PLATFORM_PROFILE'] = os.environ.get('PLATFORM_PROFILE', None) or profile
    kivy_collection.po(ctx)
    kivy_collection.mo(ctx)
    runpy.run_module('main', run_name='__main__', alter_sys=True)
