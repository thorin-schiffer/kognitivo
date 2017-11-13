from kivy.core.text import LabelBase
import kivy
from kivy.config import Config


def configure():
    import settings
    kivy.require(settings.KIVY_VERSION_REQUIRE)
    Config.set('kivy', 'log_level', settings.KIVY_LOG_LEVEL)
    if getattr(settings, 'KIVY_GRAPHICS_WIDTH') is not None:
        Config.set('graphics', 'width', settings.KIVY_GRAPHICS_WIDTH)
    if getattr(settings, 'KIVY_GRAPHICS_HEIGHT') is not None:
        Config.set('graphics', 'height', settings.KIVY_GRAPHICS_HEIGHT)

    for font in settings.KIVY_FONTS:
        LabelBase.register(**font)

    with open("version.txt") as f:
        settings.VERSION = f.read().split("%")[0]
