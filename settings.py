import os
from kivy.utils import platform, get_color_from_hex
from collections import OrderedDict

# Overall development version marker. Used in many different places, think of it as of DEBUG in Django
DEVELOPMENT_VERSION = True

# Kivy inspector toggle https://kivy.org/docs/api-kivy.modules.inspector.html
INSPECT = True
if 'KIVY_UNITTEST' not in os.environ and 'INVOKE' not in os.environ and DEVELOPMENT_VERSION:
    from kivy.app import App

    assert App.get_running_app() is not None, "settings should be imported after app instantiation (needed for testing)"

if os.environ.get("PLATFORM_PROFILE"):
    PROFILE = os.environ.get("PLATFORM_PROFILE")
else:
    with open("version.txt") as f:
        VERSION = f.read()
        PROFILE = VERSION.split("%")[1]

# Python performance tracker. Shows a label with overall statistics about python modules and kivy widgets created
SHOW_STATS = False

PROJECT_DIR = os.path.dirname(__file__)


KIVY_VERSION_REQUIRE = '1.10.0'
KIVY_GRAPHICS_HEIGHT = None
KIVY_GRAPHICS_WIDTH = None

# Kivy fonts config. Those options are passed to LabelBase instance
KIVY_FONTS = [
    {
        "name": "RobotoCondensed",
        "fn_regular": "data/fonts/RobotoCondensed-Light.ttf",
        "fn_bold": "data/fonts/RobotoCondensed-Regular.ttf",
        "fn_italic": "data/fonts/RobotoCondensed-LightItalic.ttf",
        "fn_bolditalic": "data/fonts/RobotoCondensed-Italic.ttf"
    }, {
        "name": "glyphicons",
        "fn_regular": "data/fonts/glyphicons-halflings-regular.ttf"
    },
]

# Default config being  written to the kognitivo.ini if no config existed before
KIVY_DEFAULT_CONFIG = {
    'preferences': {
        'enable_notifications': "1",
        'morning_notification_time': "09:00",
        'lunch_notification_time': "13:00",
        'evening_notification_time': "19:00",
        'language': 'system',
        'google_auto_login': "0",
        'google_logout': "1",
        'sound': "1",
        'font_size': 'normal',
        'vibration': "1"
    }
}

# Default font name
KIVY_DEFAULT_FONT = "RobotoCondensed"

# Default log kivy level
KIVY_LOG_LEVEL = "info" if not DEVELOPMENT_VERSION else "debug"

# database name
DATABASE_NAME = 'db.sqlite3'

# database path
DATABASE_PATH = os.path.join(PROJECT_DIR, DATABASE_NAME)  # if none, project path is used

# screens
ACTIVITY_SHOW_STATS_PERIOD = 30  # days

# Default colors
TEXT_COLOR = get_color_from_hex("666666ff")
TEXT_COLOR_SEMITRANSPARENT = get_color_from_hex("66666680")
TEXT_COLOR_QUASITRANSPARENT = get_color_from_hex("6666660A")
FILL_COLOR = get_color_from_hex("7e7edcff")
FILL_COLOR_SEMITRANSPARENT = get_color_from_hex("7e7edc80")
FILL_COLOR_QUASITRANSPARENT = get_color_from_hex("7e7edc33")

ACTIVITY_COLORS_TRANSPARENT = {
    "a": get_color_from_hex("66666650"),
    "t": get_color_from_hex("55d40050"),
    "r": get_color_from_hex("00aad450"),
    "m": get_color_from_hex("ff7f2a50"),
    None: FILL_COLOR_SEMITRANSPARENT
}

ACTIVITY_COLORS = {
    "a": get_color_from_hex("666666FF"),
    "t": get_color_from_hex("55d400FF"),
    "r": get_color_from_hex("00aad4FF"),
    "m": get_color_from_hex("ff7f2aFF"),
    None: FILL_COLOR
}

# Google achievement ids, those are doubled in patch/android/kognitivo/res/values/ids.xml,
# because reimporting those values from android resources management doesn't seem to be the best
# solution. Probably the best would be to interfere into the python for android template processing
GOOGLE_PLAY_ACHIEVEMENT_IDS = {
    "faithful_comrade": "CgkI2cSGw5UKEAIQAQ",
    "addicted": "CgkI2cSGw5UKEAIQAg",
    "sergeant_cognitive": "CgkI2cSGw5UKEAIQAw",
    "major_cognitive": "CgkI2cSGw5UKEAIQBA",
    "lieutenant_cognitive": "CgkI2cSGw5UKEAIQBQ",
    "colonel_cognitive": "CgkI2cSGw5UKEAIQBg",
    "general_cognitive": "CgkI2cSGw5UKEAIQBw",
    "curious": "CgkI2cSGw5UKEAIQCA",
    "supporter": "CgkI2cSGw5UKEAIQCQ",
    "social_contributor": "CgkI2cSGw5UKEAIQCg"
}

# the same with leaderboards. At the moment the only one is active
GOOGLE_PLAY_LEADERBOARD_IDS = {
    "league_of_brains": "CgkI2cSGw5UKEAIQDw"
}

# leaderboard to show in menu
LEADERBOARD = "league_of_brains"

# scale to use when efficiency is not based on average values
LOW_DATA_EFFICIENCY_SCALE = 10

# active languages
LANGUAGES = ['en', 'ru', 'de', 'es', 'ua', 'it']

# different URLs
STORE_URL = "https://play.google.com/store/apps/details?id=org.kognitivo.kognitivo"
MORE_APPS_URL = "https://play.google.com/store/apps/developer?id=Sergey+Cheparev"
FACEBOOK_PAGE_URL = "https://www.facebook.com/kognitivo"
TERMS_AND_CONDITIONS_URL = "http://kognitivoapp.com/terms-and-conditions/"
PRIVACY_POLICY_URL = "http://kognitivoapp.com/privacy-policy/"
BETA_TESTERS_GROUP_URL = "https://plus.google.com/communities/101393177085276650344"

# initial storage state
DEFAULT_STORAGE_CONFIG = {
    "starts": {"count": 0},
    "feedback": {"status": None},
    "facebook_like": {"status": None},
    "sessions": {"started": 0, "finished": 0},
    "task_records": {}
}
# google analytics
GOOGLE_ANALYTICS_TRACKING_ID = "UA-46490357-2"

# super fancy string literals
ANALYTICS_FAMILY = "a"
ATTENTION_FAMILY = "t"
REACTION_FAMILY = "r"
MEMORY_FAMILY = "m"

# tasks amount per test
TASKS_PER_TEST = 4

# tasks config
TASKS = {
    'division_calculation': {
        "class": "task_widgets.calculation.division.DivisionCalculation",
        "families": ANALYTICS_FAMILY,
        "purchasable": True
    },
    'multiplication_calculation': {
        "class": "task_widgets.calculation.multiplication.MultiplicationCalculation",
        "families": ANALYTICS_FAMILY,
        "purchasable": True
    },
    'numbers_calculation': {
        "class": "task_widgets.calculation.numbers_calculation.NumbersCalculation",
        "families": ANALYTICS_FAMILY,
        "purchasable": False
    },
    'percents_calculation': {
        "class": "task_widgets.calculation.percents.PercentsCalculation",
        "families": ANALYTICS_FAMILY,
        "purchasable": True
    },
    'time_calculation': {
        "class": "task_widgets.calculation.time_calculation.TimeCalculation",
        "families": ANALYTICS_FAMILY,
        "purchasable": False
    },
    'time_calculation_minutes': {
        "class": "task_widgets.calculation.time_calculation_minutes.TimeCalculationMinutes",
        "families": ANALYTICS_FAMILY,
        "purchasable": True
    },
    'time_subtraction': {
        "class": "task_widgets.calculation.time_subtraction.TimeSubtraction",
        "families": ANALYTICS_FAMILY,
        "purchasable": True
    },
    'find_color': {
        "class": "task_widgets.find_in_table.find_color.FindColor",
        "families": ATTENTION_FAMILY,
        "purchasable": False
    },
    'find_contraversal': {
        "class": "task_widgets.find_in_table.find_contraveral.FindContraversal",
        "families": ATTENTION_FAMILY + ANALYTICS_FAMILY,
        "purchasable": False
    },
    'find_figures': {
        "class": "task_widgets.find_in_table.find_figures.FindFigures",
        "families": ATTENTION_FAMILY + ANALYTICS_FAMILY,
        "purchasable": True
    },
    'find_letter': {
        "class": "task_widgets.find_in_table.find_letter.FindLetter",
        "families": ATTENTION_FAMILY,
        "purchasable": False
    },
    'find_number': {
        "class": "task_widgets.find_in_table.find_number.FindNumber",
        "families": ATTENTION_FAMILY,
        "purchasable": False
    },
    'find_primer': {
        "class": "task_widgets.find_in_table.find_primer.FindPrimer",
        "families": ATTENTION_FAMILY + ANALYTICS_FAMILY,
        "purchasable": True
    },
    'find_symbol': {
        "class": "task_widgets.find_in_table.find_symbol.FindSymbol",
        "families": ATTENTION_FAMILY,
        "purchasable": False
    },
    'find_color_dynamic': {
        "class": "task_widgets.find_in_table_dynamic.find_color_dynamic.FindColorDynamic",
        "families": ATTENTION_FAMILY + REACTION_FAMILY,
        "purchasable": False
    },
    'find_letter_dynamic': {
        "class": "task_widgets.find_in_table_dynamic.find_letter_dynamic.FindLetterDynamic",
        "families": ATTENTION_FAMILY + REACTION_FAMILY,
        "purchasable": False
    },
    'find_number_dynamic': {
        "class": "task_widgets.find_in_table_dynamic.find_number_dynamic.FindNumberDynamic",
        "families": ATTENTION_FAMILY + REACTION_FAMILY,
        "purchasable": False
    },
    'find_symbol_dynamic': {
        "class": "task_widgets.find_in_table_dynamic.find_symbol_dynamic.FindSymbolDynamic",
        "families": ATTENTION_FAMILY + REACTION_FAMILY,
        "purchasable": False
    },
    'color_sequence': {
        "class": "task_widgets.remember_sequence.color_sequence.ColorSequence",
        "families": MEMORY_FAMILY,
        "purchasable": False
    },
    'letter_sequence': {
        "class": "task_widgets.remember_sequence.letter_sequence.LetterSequence",
        "families": MEMORY_FAMILY,
        "purchasable": False
    },
    'number_sequence': {
        "class": "task_widgets.remember_sequence.number_sequence.NumberSequence",
        "families": MEMORY_FAMILY,
        "purchasable": False
    },
    'symbol_sequence': {
        "class": "task_widgets.remember_sequence.symbol_sequence.SymbolSequence",
        "families": MEMORY_FAMILY,
        "purchasable": False
    },
    'reverse_letters': {
        "class": "task_widgets.reverse_sequence.reverse_letters.ReverseLetters",
        "families": ANALYTICS_FAMILY + MEMORY_FAMILY,
        "purchasable": False
    },
    'reverse_numbers': {
        "class": "task_widgets.reverse_sequence.reverse_numbers.ReverseNumbers",
        "families": ANALYTICS_FAMILY + MEMORY_FAMILY,
        "purchasable": False
    },
    'reverse_symbols': {
        "class": "task_widgets.reverse_sequence.reverse_symbols.ReverseSymbols",
        "families": ANALYTICS_FAMILY + MEMORY_FAMILY,
        "purchasable": False
    },
    'color_table': {
        "class": "task_widgets.table_element.color_table.ColorTable",
        "families": MEMORY_FAMILY + ATTENTION_FAMILY,
        "purchasable": False
    },
    'letter_table': {
        "class": "task_widgets.table_element.letter_table.LetterTable",
        "families": MEMORY_FAMILY + ATTENTION_FAMILY,
        "purchasable": False
    },
    'number_table': {
        "class": "task_widgets.table_element.number_table.NumberTable",
        "families": MEMORY_FAMILY + ATTENTION_FAMILY,
        "purchasable": False
    },
    'symbol_table': {
        "class": "task_widgets.table_element.symbol_table.SymbolTable",
        "families": MEMORY_FAMILY + ATTENTION_FAMILY,
        "purchasable": False
    },
    'white_squares': {
        "class": "task_widgets.white_squares.WhiteSquares",
        "families": REACTION_FAMILY + ATTENTION_FAMILY,
        "purchasable": False
    },
    'tip_ball': {
        "class": "task_widgets.tip_ball.TipBall",
        "families": REACTION_FAMILY,
        "purchasable": False
    }
}

# sound toggle. Some platforms wouldn't support sounds out of box
SOUND_ENABLED = True

# sounds config
SOUNDS = {
    "tap": "data/sounds/tap.mp3",
    "success": "data/sounds/success.mp3",
    "start": "data/sounds/start.mp3",
    "fail": "data/sounds/fail.mp3",
    "test_finished": "data/sounds/test_finished.mp3",
}

# purchases config
if DEVELOPMENT_VERSION:
    INAPP_PURCHASES = OrderedDict((
        ("lifetime_premium", {
            "icon": "atlas://data/atlas/purchases/lifetime_premium",
            "unlocks_tasks": None,
            "type": "inapp"
        }),
        ("premium_subscription", {
            "icon": "atlas://data/atlas/purchases/premium_subscription",
            "unlocks_tasks": None,
            "type": "subs"
        }),
        ("android.test.purchased", {
            "icon": "atlas://data/atlas/purchases/lifetime_premium",
            "unlocks_tasks": None,
            "type": "inapp"
        }),
        # ("android.test.purchased", {
        #     "icon": "atlas://data/atlas/purchases/premium_subscription",
        #     "unlocks_tasks": None,
        #     "type": "subs"
        # }), # this causes 500 on google side :D
        ("android.test.canceled", {
            "icon": "atlas://data/atlas/purchases/time_arena",
            "unlocks_tasks": ["find_figures", "find_primer"],
            "type": "inapp"
        }),
        ("android.test.refunded", {
            "icon": "atlas://data/atlas/purchases/clash_arena",
            "unlocks_tasks": ["division_calculation", "percents_calculation", "multiplication_calculation"],
            "type": "inapp"
        }),
        ("analytics_arena_pack", {
            "icon": "atlas://data/atlas/purchases/calculation_arena",
            "unlocks_tasks": ["division_calculation", "percents_calculation", "multiplication_calculation"],
            "type": "inapp"
        }),
        ("time_arena_pack", {
            "icon": "atlas://data/atlas/purchases/time_arena",
            "unlocks_tasks": ["time_subtraction", "time_calculation_minutes"],
            "type": "inapp"
        }),
        ("clash_arena_pack", {
            "icon": "atlas://data/atlas/purchases/clash_arena",
            "unlocks_tasks": ["find_figures", "find_primer"],
            "type": "inapp"
        }),
    ))
else:
    INAPP_PURCHASES = OrderedDict([
        ("lifetime_premium", {
            "icon": "atlas://data/atlas/purchases/lifetime_premium",
            "unlocks_tasks": None,
            "type": "inapp"
        }),
        ("premium_subscription", {
            "icon": "atlas://data/atlas/purchases/premium_subscription",
            "unlocks_tasks": None,
            "type": "subs"
        }),
        ("analytics_arena_pack", {
            "icon": "atlas://data/atlas/purchases/calculation_arena",
            "unlocks_tasks": ["division_calculation", "percents_calculation", "multiplication_calculation"],
            "type": "inapp"
        }),
        ("time_arena_pack", {
            "icon": "atlas://data/atlas/purchases/time_arena",
            "unlocks_tasks": ["time_subtraction", "time_calculation_minutes"],
            "type": "inapp"
        }),
        ("clash_arena_pack", {
            "icon": "atlas://data/atlas/purchases/clash_arena",
            "unlocks_tasks": ["find_figures", "find_primer"],
            "type": "inapp"
        }),
    ])

# sentry raven DSN
RAVEN_DSN = 'sync+https://2489b07868ba4e97b0bfabacc9dc19a2:698effaa42ba472c8b0cd1ced1df0882@sentry.io/243917'

# platform and profile overloads
try:
    platform_settings = "from settings_" + str(platform) + " import *"
    exec platform_settings
except ImportError:
    pass

if PROFILE:
    try:
        profile_settings = "from settings_profile_" + PROFILE + " import *"
        exec profile_settings
    except ImportError:
        pass
