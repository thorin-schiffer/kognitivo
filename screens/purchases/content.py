from kivy import Logger
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.properties import StringProperty, ObjectProperty, BooleanProperty

from library_widgets import ImageButton
from utils import import_kv, _

import_kv(__file__)


class BuyButton(ImageButton):
    pass


class TaskTypeSlide(BoxLayout):
    tutorial = ObjectProperty()
    title = ObjectProperty()
    description = ObjectProperty()
    task_key = StringProperty()
    running = BooleanProperty(False)

    def __init__(self, task_key, **kwargs):
        from library_widgets import TutorialAnimator

        self.tutorial = TutorialAnimator(task_key=task_key)
        self.tasks = {
            "find_figures": {
                "title": _("Figure Out"),
                "description": _("Find all correctly named figures")
            },
            "find_primer": {
                "title": _("Right Choice"),
                "description": _("Find all right expressions")
            },
            "division_calculation": {
                "title": _("Super Brain: Division"),
                "description": _("Calculate the result!")
            },
            "percents_calculation": {
                "title": _("Super Brain: Percents"),
                "description": _("Calculate the result!")
            },
            "multiplication_calculation": {
                "title": _("Multi Super Brain"),
                "description": _("Calculate the result!")
            },
            "time_subtraction": {
                "title": _("Time Machine: Subtraction"),
                "description": _("Time Machine: Subtraction")
            },
            "time_calculation_minutes": {
                "title": _("Time Machine: Last Minutes"),
                "description": _("Add the interval in minutes of the\n right clock to the left one")
            }
        }

        super(TaskTypeSlide, self).__init__(task_key=task_key, **kwargs)
        self.title.text = self.tasks[task_key]['title']
        self.description.text = self.tasks[task_key]['description']
        self.add_widget(self.tutorial, 2)

    def start_animation(self):
        self.tutorial.reset()
        self.tutorial.start()
        self.running = True

    def stop_animation(self):
        self.tutorial.stop()
        self.running = False


class PromoCarousel(Carousel):
    item_id = StringProperty()
    TASKS_SLIDE_TIMEOUT = 7
    is_running = BooleanProperty(False)

    def on_item_id(self, carousel, item_id):
        import settings

        unlocks_tasks = settings.INAPP_PURCHASES[self.item_id].get('unlocks_tasks', [])
        if unlocks_tasks is None:
            unlocks_tasks = [key for key in settings.TASKS if settings.TASKS[key].get('purchasable', False)]

        for task_key in unlocks_tasks:
            self.add_widget(TaskTypeSlide(task_key=task_key))

        # can't use on_current_slide because of dynamic creating the slides
        self.bind(current_slide=self.load_next_slide)

    def load_next_slide(self, carousel, task_slide):
        from kivy.clock import Clock

        for slide in self.slides:
            slide.stop_animation()

        self.current_slide.start_animation()
        Clock.unschedule(self.load_next)
        Clock.schedule_once(self.load_next, timeout=self.TASKS_SLIDE_TIMEOUT)

    def start(self):
        self.load_next_slide(self, self.current_slide)
        self.is_running = True

    def stop(self):
        self.current_slide.stop_animation()
        from kivy.clock import Clock

        Clock.unschedule(self.load_next)
        self.is_running = False


class PurchaseDetailScreen(Screen):
    icon = StringProperty()
    title = StringProperty()
    description = StringProperty()
    price = StringProperty()
    item_id = StringProperty()
    purchased = BooleanProperty(None, allownone=True)
    buy_button = ObjectProperty()
    promo_carousel = ObjectProperty()

    def __init__(self, item_id, **kw):
        import settings
        import re

        config = settings.INAPP_PURCHASES[item_id]
        store_information = App.get_running_app().billing.get_item_info(item_id)
        self.icon = config['icon']
        self.description = store_information['description']
        self.price = store_information['price']
        self.title = re.sub(r" \(.*?\)", "", store_information['title'])
        super(PurchaseDetailScreen, self).__init__(item_id=item_id, **kw)

    def on_enter(self, *args):
        self.promo_carousel.start()

    def on_leave(self, *args):
        self.promo_carousel.stop()

    def mark_purchased(self, purchase, *args, **kwargs):
        assert self.item_id == purchase['productId']
        self.purchased = True

    def thank_you_popup(self, purchase, *args):
        app = App.get_running_app()
        app.tracker.send_event('purchase', 'thankyou', purchase['productId'])
        ThankYouPopup().open()
        app.manager.to_screen('purchases')

    def buy(self):
        import settings

        app = App.get_running_app()
        if not self.purchased:
            app.billing.buy(self.item_id,
                            callbacks=[
                                self.mark_purchased,
                                self.thank_you_popup
                            ])
            app.tracker.send_event('purchase', 'menu', self.item_id)
        else:
            app.manager = App.get_running_app().manager
            tasks_screen = app.manager.get_screen("tasks")
            if settings.INAPP_PURCHASES[self.item_id]['unlocks_tasks'] is not None:
                tasks_screen.tasks = settings.INAPP_PURCHASES[self.item_id]['unlocks_tasks']
            tasks_screen.family = None
            app.manager.to_screen('tasks')

    def on_purchased(self, instance, value):
        if value:
            self.buy_button.source = "atlas://data/atlas/purchases/play_now"
            self.buy_button.text = _("TRY NOW")
        else:
            self.buy_button.source = "atlas://data/atlas/menu/buy"


class ThankYouPopup(Popup):
    def open(self, *largs):
        from kivy.clock import Clock

        super(ThankYouPopup, self).open(*largs)
        Clock.schedule_once(self.dismiss, timeout=1)


class InternetProblemsScreen(Screen):
    pass


class PurchasesContainer(ScreenManager):
    popup = ObjectProperty()

    def __init__(self, **kwargs):
        super(PurchasesContainer, self).__init__(**kwargs)
        import settings

        billing = App.get_running_app().billing
        available_items = billing.get_available_skus()
        if not available_items:
            self.add_widget(InternetProblemsScreen())
            return
        Logger.info("Purchases: available items: %s" % ",".join(available_items))
        for sku in settings.INAPP_PURCHASES.keys():
            if sku in available_items:
                screen = PurchaseDetailScreen(name="purchases_" + sku,
                                              item_id=sku)
                screen.download_url = settings.INAPP_PURCHASES[sku].get('download_url')
                screen.purchased = sku in billing.get_purchased_items()
                self.add_widget(screen)

    def stop(self):
        if isinstance(self.current_screen, PurchaseDetailScreen):
            self.current_screen.promo_carousel.stop()

    def start(self):
        if isinstance(self.current_screen, PurchaseDetailScreen):
            self.current_screen.promo_carousel.start()
