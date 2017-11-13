# this module is a mess, 80% of all errors refer to unwritable data directory.
# reliably writable directory should be provided by kivy IMHO though

from jnius import autoclass
import os
from kivy import Logger
from utils import writable
from settings import DATABASE_NAME

# see https://github.com/kivy/kivy/issues/5412
SOUND_ENABLED = False

try:
    Environment = autoclass('android.os.Environment')
    path = os.path.join(unicode(Environment.getExternalStorageDirectory().getAbsolutePath()), DATABASE_NAME)
except Exception:
    path = ""

if writable(path):
    DATABASE_PATH = path
else:
    from settings import DATABASE_PATH
    if not writable(DATABASE_PATH):
        variants = ("/sdcard", "./", "/data/data/kognitivo.kognitivo.org")
        for variant in variants:
            path = os.path.join(variant, DATABASE_NAME)
            Logger.warning("Android Settings: try database path %s" % path)
            if writable(path):
                DATABASE_PATH = path
                break
            else:
                DATABASE_PATH = None

        if not DATABASE_PATH:
            try:
                Context = autoclass('android.content.Context')
                path = os.path.join(unicode(Context.getFilesDir()), DATABASE_NAME)
            except Exception:
                path = ""
            if writable(path):
                DATABASE_PATH = path
            else:
                raise RuntimeError("No writable paths for database can be found")
