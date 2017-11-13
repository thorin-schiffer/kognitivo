# generic widgets should be placed here
import os

from kivy import Logger, platform
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.factory import Factory
from kivy.event import EventDispatcher
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.image import Image, AsyncImage
from kivy.properties import StringProperty, ListProperty, OptionProperty, NumericProperty, BooleanProperty
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy.clock import Clock

from utils import import_kv

import_kv(__file__)


class AnimationMixin(EventDispatcher):
    animation = ObjectProperty()

    def inner_animation_completed_handler(self, *_):
        self.dispatch('on_animation_completed')
        pass

    def on_animation_completed(self):
        pass

    def on_animation(self, _, value):
        value.bind(on_complete=self.inner_animation_completed_handler)

    def start_animation(self):
        self.animation.cancel(self)
        self.animation.start(self)

    def __init__(self, **kwargs):
        super(AnimationMixin, self).__init__(**kwargs)
        self.register_event_type('on_animation_completed')


Factory.register('AnimationMixin', AnimationMixin)


class OnPressAnimationMixin(ButtonBehavior, AnimationMixin):
    def __init__(self, **kwargs):
        super(OnPressAnimationMixin, self).__init__(**kwargs)
        self.bind(on_press=self._on_press)

    def _on_press(self, *_):
        self.animation.start(self)


class OnPressBlinkMixin(OnPressAnimationMixin):
    pass


Factory.register('OnPressBlinkMixin', OnPressBlinkMixin)


class ImageButton(ButtonBehavior, AsyncImage):
    name = StringProperty()

    def on_press(self):
        App.get_running_app().sounds['tap'].play()


class TitledMixin(EventDispatcher):
    title = StringProperty("")
    orientation = OptionProperty("upper", options=["upper", "lower", "right", "left"])
    shift = NumericProperty(0.5)
    label = ObjectProperty()

    def layout_label(self, instance, _):
        if self.orientation in ["upper", "lower"]:
            y_shift = instance.height * self.shift + self.label.font_size
            if instance.orientation == "lower":
                y_shift = -y_shift
            instance.label.center = (instance.center[0], instance.center[1] + y_shift)

        if self.orientation in ["right", "left"]:
            x_shift = instance.width * self.shift + self.label.font_size
            if instance.orientation == "left":
                x_shift = -x_shift
            instance.label.center = (instance.center[0] + x_shift, instance.center[1])

    def __init__(self, **kwargs):
        super(TitledMixin, self).__init__(**kwargs)
        self.bind(size=self.layout_label,
                  pos=self.layout_label)


class CircleDiagram(FloatLayout):
    part = NumericProperty(0)
    inner_part = NumericProperty()
    label = ObjectProperty()
    color = ListProperty()
    COEFFICIENT = 0.8

    def _draw_circle(self, d, part):
        from kivy.graphics import Ellipse

        pos = (self.pos[0] + self.size[0] / 2 - d / 2,
               self.pos[1] + self.size[1] / 2 - d / 2)
        Ellipse(size=(d, d), pos=pos, angle_start=0, angle_end=part * 360, segments=45)

    def on_resize(self, instance, value):
        from kivy.graphics import Color

        self.canvas.before.clear()
        if self.inner_part > 0:
            with self.canvas.before:
                Color(*self.color)
                d = min(instance.size)
                for _ in range(int(self.inner_part)):
                    self._draw_circle(d, 1)
                    d *= self.COEFFICIENT
                self._draw_circle(d, self.inner_part - int(self.inner_part))

    def on_inner_part(self, instance, value):
        instance.label.text = "%.0f %%" % (value * 100)

    def on_part(self, instance, value):
        Animation(inner_part=value, t=self.transition, d=self.duration).start(self)

    def __init__(self, **kwargs):
        super(CircleDiagram, self).__init__(**kwargs)
        self.bind(size=self.on_resize,
                  pos=self.on_resize,
                  inner_part=self.on_resize)


class ColorSquare(Widget):
    RADIUS = .1
    background_color = ListProperty()

    def fill_canvas(self):
        self.canvas.before.clear()
        from kivy.graphics.vertex_instructions import Rectangle, Ellipse
        from kivy.graphics.context_instructions import Color

        with self.canvas:
            self._color = Color(*self.background_color)
            self.rectangles = [Rectangle(), Rectangle(), Rectangle(), Rectangle(), Rectangle()]
            self.ellipses = [Ellipse(angle_start=270, angle_end=0, segments=10),
                             Ellipse(angle_start=0, angle_end=90, segments=10),
                             Ellipse(angle_start=90, angle_end=180, segments=10),
                             Ellipse(angle_start=180, angle_end=270, segments=10)]

    def relocate(self, *args, **kwargs):
        if not self.rectangles:
            return
        edge = min(self.size)
        radius = edge * self.RADIUS
        self.rectangles[0].pos = (self.center[0] - edge / 2 + radius, self.center[1] - edge / 2 + radius)
        self.rectangles[0].size = (edge - 2 * radius, edge - 2 * radius)

        self.rectangles[1].pos = (self.center[0] - edge / 2 + radius, self.center[1] - edge / 2)
        self.rectangles[1].size = (edge - 2 * radius, radius)

        self.rectangles[2].pos = (self.center[0] - edge / 2 + radius, self.center[1] + edge / 2 - radius)
        self.rectangles[2].size = (edge - 2 * radius, radius)

        self.rectangles[3].pos = (self.center[0] - edge / 2, self.center[1] - edge / 2 + radius)
        self.rectangles[3].size = (radius, edge - 2 * radius)

        self.rectangles[4].pos = (self.center[0] + edge / 2 - radius, self.center[1] - edge / 2 + radius)
        self.rectangles[4].size = (radius, edge - 2 * radius)

        self.ellipses[0].pos = (self.center[0] - edge / 2, self.center[1] + edge / 2 - radius * 2)
        self.ellipses[0].size = (radius * 2, radius * 2)

        self.ellipses[1].pos = (
            self.center[0] + edge / 2 - radius * 2, self.center[1] + edge / 2 - radius * 2)
        self.ellipses[1].size = (radius * 2, radius * 2)

        self.ellipses[2].pos = (self.center[0] + edge / 2 - radius * 2, self.center[1] - edge / 2)
        self.ellipses[2].size = (radius * 2, radius * 2)

        self.ellipses[3].pos = (self.center[0] - edge / 2, self.center[1] - edge / 2)
        self.ellipses[3].size = (radius * 2, radius * 2)

    def on_background_color(self, *args, **kwargs):
        if self._color:
            self._color.rgba = self.background_color

    on_size = on_pos = relocate

    def __init__(self, **kwargs):
        self.rectangles = []
        self.ellipses = []
        self._color = None
        super(ColorSquare, self).__init__(**kwargs)
        self.fill_canvas()


class MarkRedMixin(Widget):
    """
    Utility class for marking the widget borders
    """
    pass


class TrackingScreenMixin(object):
    def on_enter(self, *args):
        from kivy.app import App

        tracker = App.get_running_app().tracker
        tracker.send_screen(self)

    def on_pre_leave(self, *args):
        from kivy.app import App

        tracker = App.get_running_app().tracker
        tracker.clear_screen()


class PngAnimator(Image):
    sources = ListProperty()
    current_index = NumericProperty(0)
    playing = BooleanProperty(False)

    def reset(self):
        self.stop()
        self.current_index = 0
        self.start()

    def on_sources(self, instance, value):
        self.source = self.sources[0]

    def on_repeat(self, *args, **kwargs):
        pass

    def on_current_index(self, *args):
        self.source = self.sources[self.current_index]

    def next_source(self, _):
        if self.playing:
            if self.current_index == len(self.sources) - 1:
                self.dispatch('on_repeat')
            self.current_index = (self.current_index + 1) % len(self.sources)

    def start(self):
        Clock.unschedule(self.next_source)
        Clock.schedule_interval(self.next_source, timeout=1.)
        self.playing = True

    def stop(self):
        Clock.unschedule(self.next_source)
        self.playing = False

    def __init__(self, **kwargs):
        self.register_event_type('on_repeat')
        super(PngAnimator, self).__init__(**kwargs)


class OkPopup(Popup):
    text = StringProperty()
    ok_callback = ObjectProperty(None, allownone=True)


class OkCancelPopup(Popup):
    text = StringProperty()
    ok_callback = ObjectProperty(None, allownone=True)
    cancel_callback = ObjectProperty(None, allownone=True)


class CrashPopup(Popup):
    text = StringProperty()
    ok_callback = ObjectProperty(None, allownone=True)


class LoadingWidget(BoxLayout):
    icon = StringProperty()

    def _detach(self, *args, **kwargs):
        self.parent.remove_widget(self)

    def hide(self, content):
        content.opacity = 0
        self.parent.add_widget(content)

        animation = Animation(opacity=1, d=.5)
        animation.start(content)
        animation = Animation(opacity=0, d=.5)
        animation.bind(on_complete=self._detach)
        animation.start(self)


class TutorialAnimator(PngAnimator):
    task_key = StringProperty()

    def on_task_key(self, instance, value):
        path = "data/img/task_tutorials/%s" % self.task_key
        paths = [os.path.join(path, f) for f in os.listdir(path)]
        paths.sort()
        self.sources = paths


class DidYouKnowLabel(Label):
    texts = None

    def _set_text(self):
        from random import choice

        text = choice(DidYouKnowLabel.texts)

        self.text = text['text']
        self.on_ref_press = text['action']

    @staticmethod
    def to_purchases_screen(*args, **kwargs):
        App.get_running_app().manager.to_screen('purchases')

    def mail(self, ref, *args, **kwargs):
        try:
            import webbrowser
            from utils import _  # noqa F401 looks like i18n on mail subject wouldn't work without this import

            webbrowser.open("mailto:sergey@cheparev.com?subject=%s" % ref)
        except Exception:
            Logger.error("Browser: could not start mailto...")

    def facebook(self, *args, **kwargs):
        try:
            import webbrowser
            import settings

            webbrowser.open(settings.FACEBOOK_PAGE_URL)
        except Exception:
            Logger.error("Browser: could not start facebook...")

    def beta_testers_group(self, *args, **kwargs):
        try:
            import webbrowser
            import settings

            webbrowser.open(settings.BETA_TESTERS_GROUP_URL)
        except Exception:
            Logger.error("Browser: could not start google group...")

    def settings(self, *args, **kwargs):
        App.get_running_app().open_settings()

    def __init__(self, **kwargs):
        super(DidYouKnowLabel, self).__init__(**kwargs)
        from utils import _
        import settings

        if not DidYouKnowLabel.texts:
            DidYouKnowLabel.texts = [
                {
                    "text": _(
                        u"Found a bug? Let me know: "
                        u"[ref=Kognitivo: I found a bug][b][font=glyphicons]\uE127[/font] sergey@cheparev.com[/b][/ref]"),
                    "action": self.mail
                },
                {
                    "text": _(u"Got a feature idea? "
                              u"Share it on [ref=feature][b][font=glyphicons]\uE127[/font] FACEBOOK[/b][/ref]"),
                    "action": self.facebook
                },
                {
                    "text": _(u"Found a misspelled word? Let me know: "
                              u"[ref=Kognitivo: Grammar][b][font=glyphicons]\uE127[/font] sergey@cheparev.com[/b][/ref]"),
                    "action": self.mail
                },
                {
                    "text": _(
                        u"Change font size in [ref=font][b][font=glyphicons]\uE127[/font]settings[/b][/ref] "
                        u"if it is too big or to small"),
                    "action": self.settings
                },
                {
                    "text": _(
                        u"Want most recent features? Become a"
                        u" [ref=tester][b][font=glyphicons]\uE127[/font]tester[/b][/ref]"),
                    "action": self.beta_testers_group
                },
                {
                    "text": _(
                        u"The more you practice, the more accurate is the statistics"),
                    "action": None
                },
            ]
            if platform == 'android' and not settings.PROFILE:
                DidYouKnowLabel.texts += [
                    {
                        "text": _(u"Need more tasks? "
                                  u"Take a look [ref=purchase][b][font=glyphicons]\uE127[/font] HERE[/b][/ref]"),
                        "action": self.to_purchases_screen
                    },
                    {
                        "text": _(u"Try 7 days of full features for free with "
                                  u"[ref=premium_subscription][b][font=glyphicons]"
                                  u"\uE127[/font]premium subscription[/b][/ref]"),
                        "action": self.to_purchases_screen
                    },
                    {
                        "text": _(u"Connect your [ref=google][b][font=glyphicons]\uE127[/font]Google account[/b][/ref] "
                                  u"in order to compete with friends"),
                        "action": self.settings
                    },
                ]
        self._set_text()


class TutorialContentWidget(ModalView):
    point_widget = ObjectProperty()
    label = ObjectProperty()

    def on_touch_down(self, touch):
        App.get_running_app().sounds['success'].play()
        self.dismiss()
        return True


class TutorialMixin(Widget):
    tutorial_text = StringProperty()
    _tutorial_content = ObjectProperty()
    tutorial_position = ObjectProperty()
    tutorial_size = ListProperty()
    point_screen = StringProperty('activity')

    def __init__(self, **kwargs):
        self.register_event_type('on_tutorial_start')
        self.register_event_type('on_tutorial_finish')
        super(TutorialMixin, self).__init__(**kwargs)
        self.window = None
        self.screen = None
        self._background_color = None
        self._next_widgets = None
        self._left_rectangle = None
        self._right_rectangle = None
        self._bottom_rectangle = None
        self._top_rectangle = None
        self._tutorial_stopped = False

    def _to_next_tutorial(self, *args):
        if self._next_widgets:
            next_widget = self._next_widgets.pop(0)
            next_widget.show_tutorial(self._next_widgets)

    def stop_tutorial(self):
        if self._next_widgets:
            del self._next_widgets[:]
        self._tutorial_stopped = True

    def hide_tutorial(self, *args):
        animation = Animation(rgba=(1, 1, 1, 0), d=.5, t='in_out_cubic')
        animation.start(self._background_color)
        animation = Animation(color=(1, 1, 1, 0), d=.5, t='in_out_cubic')

        if self._next_widgets:
            animation.bind(on_complete=self._to_next_tutorial)
        else:
            if not self._tutorial_stopped:
                self.dispatch('on_tutorial_finish')
        animation.start(self._tutorial_content.label)
        self.unbind(size=self._place_rectangles, pos=self._place_rectangles)

    def on_tutorial_start(self):
        pass

    def on_tutorial_finish(self):
        pass

    def _place_rectangles(self, *args):
        self._left_rectangle.size = (self.x, self.window.height)
        self._right_rectangle.pos = (self.x + self.width, 0)
        self._right_rectangle.size = (
            self.window.width - self.x - self.width,
            self.window.height
        )
        self._bottom_rectangle.pos = (self.x, 0)
        self._bottom_rectangle.size = (self.width, self.y)
        self._top_rectangle.pos = (self.x, self.y + self.height)
        self._top_rectangle.size = (self.width, self.y + self.height)

    def show_tutorial(self, next_widgets=None):
        self.screen = App.get_running_app().manager.current_screen
        if self.screen and not self.screen.name == self.point_screen:
            self.stop_tutorial()
            return

        self.dispatch('on_tutorial_start')
        self._next_widgets = next_widgets
        from kivy.graphics.context_instructions import Color
        from kivy.graphics.vertex_instructions import Rectangle
        from kivy.animation import Animation
        self.window = App.get_running_app().root_window

        with self.window.canvas:
            self._background_color = Color(1, 1, 1, 0)
            self._left_rectangle = Rectangle()
            self._right_rectangle = Rectangle()
            self._bottom_rectangle = Rectangle()
            self._top_rectangle = Rectangle()
        self._place_rectangles()
        animation = Animation(rgba=(1, 1, 1, 1), d=.25, t='in_out_cubic')
        animation.bind(on_complete=self._show_tutorial_content)
        animation.start(self._background_color)
        self.bind(size=self._place_rectangles, pos=self._place_rectangles)

    def _show_tutorial_content(self, *args):
        self._tutorial_content = TutorialContentWidget(
            point_widget=self,
        )
        self._tutorial_content.bind(on_dismiss=self.hide_tutorial)
        self._tutorial_content.open()

        import settings
        animation = Animation(color=settings.TEXT_COLOR, d=.25, t='in_out_cubic')
        animation.start(self._tutorial_content.label)
