from collections import OrderedDict

import pytest

import control
from tests.assertions import assert_bought, assert_tracker_event_sent
from tests.markers import inapp_purchase
from tests.test_utils import override_settings


@pytest.fixture
def screen(running_app, root_manager):
    from screens.purchases.purchases import PurchaseScreen

    s = PurchaseScreen()
    root_manager.add_widget(s)
    return s


@pytest.fixture
def detail_screen(running_app, billing):
    from screens.purchases.content import PurchaseDetailScreen
    import settings

    item_id = settings.INAPP_PURCHASES.keys()[0]
    return PurchaseDetailScreen(item_id=item_id)


def test_enter_purchases(root_manager, screen):
    control.enter(screen)
    assert not root_manager.has_screen('menu')
    assert not root_manager.has_screen('tasks')
    assert not root_manager.has_screen('activity')
    assert screen._container is not None
    from library_widgets import LoadingWidget

    assert not any(isinstance(child, LoadingWidget) for child in screen.children)


def test_leave_purchases(root_manager, screen):
    control.enter(screen)
    control.leave(screen)
    assert not screen.container.current_screen.promo_carousel.is_running


@inapp_purchase
def test_purchase_detail_screen_build(billing, detail_screen):
    import settings

    purchase_config = settings.INAPP_PURCHASES[detail_screen.item_id]
    store_info = billing.get_item_info(detail_screen.item_id)
    assert detail_screen.icon == purchase_config['icon']
    assert detail_screen.title
    assert "KOGNITIVO Brain Trainer" not in detail_screen.title
    assert detail_screen.description == store_info["description"]
    assert detail_screen.price == store_info["price"]
    assert detail_screen.promo_carousel


@inapp_purchase
def test_purchase_detail_screen_enter(detail_screen):
    assert not detail_screen.promo_carousel.is_running
    control.enter(detail_screen)
    assert detail_screen.promo_carousel.is_running
    control.leave(detail_screen)
    assert not detail_screen.promo_carousel.is_running


@override_settings(
    INAPP_PURCHASES=OrderedDict([
        ("lifetime_premium", {
            "icon": "atlas://data/atlas/purchases/lifetime_premium",
            "unlocks_tasks": ["division_calculation", "percents_calculation", "multiplication_calculation"],
            "type": "inapp"
        })])
)
def test_purchase_promo_carousel_build_slides(running_app):
    from screens.purchases.content import PromoCarousel

    carousel = PromoCarousel()
    assert not carousel.slides
    import settings

    item_id = settings.INAPP_PURCHASES.keys()[0]
    carousel.item_id = item_id
    assert len(carousel.slides) == len(settings.INAPP_PURCHASES[item_id]['unlocks_tasks'])


@override_settings(
    INAPP_PURCHASES=OrderedDict([
        ("lifetime_premium", {
            "icon": "atlas://data/atlas/purchases/lifetime_premium",
            "unlocks_tasks": None,
            "type": "inapp"
        })])
)
def test_purchase_promo_carousel_unlocks_tasks_build_slides_none(running_app):
    from screens.purchases.content import PromoCarousel

    carousel = PromoCarousel()
    import settings

    item_id = settings.INAPP_PURCHASES.keys()[0]
    carousel.item_id = item_id
    assert len(carousel.slides) == len(
        [key for key in settings.TASKS if settings.TASKS[key].get('purchasable', False)]
    )


@inapp_purchase
def test_purchase_task_slide_build(running_app):
    from screens.purchases.content import TaskTypeSlide
    from utils import _

    slide = TaskTypeSlide(task_key='find_figures')
    assert slide.tutorial
    assert slide.title.text == _("Figure Out")
    assert slide.description.text == _("Find all correctly named figures")
    assert not slide.running
    assert not slide.tutorial.playing
    slide.start_animation()
    assert slide.running
    assert slide.tutorial.playing
    slide.stop_animation()
    assert not slide.running
    assert not slide.tutorial.playing


@inapp_purchase
def test_purchase_start_stop_control(running_app):
    from screens.purchases.content import PromoCarousel

    carousel = PromoCarousel()
    assert not carousel.slides
    import settings

    item_id = settings.INAPP_PURCHASES.keys()[0]
    carousel.item_id = item_id
    for slide in carousel.slides:
        assert not slide.tutorial.playing

    carousel.start()
    for slide in carousel.slides:
        if slide == carousel.current_slide:
            assert slide.running
            assert slide.tutorial.playing
        else:
            assert not slide.running
            assert not slide.tutorial.playing

    carousel.load_next()
    for slide in carousel.slides:
        if slide == carousel.current_slide:
            assert slide.running
            assert slide.tutorial.playing
        else:
            assert not slide.running
            assert not slide.tutorial.playing

    carousel.stop()
    for slide in carousel.slides:
        assert not slide.running
        assert not slide.tutorial.playing


@inapp_purchase
def test_purchase_detail_screen_buy(detail_screen, billing, tracker):
    from utils import _

    control.press(detail_screen.buy_button)
    assert detail_screen.buy_button.source == "atlas://data/atlas/purchases/play_now"
    assert detail_screen.buy_button.text == _("TRY NOW")
    assert_bought(billing, detail_screen.item_id,
                  callbacks=[detail_screen.mark_purchased, detail_screen.thank_you_popup])
    assert_tracker_event_sent(tracker, 'purchase', 'menu', detail_screen.item_id)


@inapp_purchase
def test_purchase_try_now_after_bought_none(root_manager, detail_screen):
    control.press(detail_screen.buy_button)
    control.press(detail_screen.buy_button)
    assert root_manager.current == 'tasks'
    tasks_screen = root_manager.get_screen('tasks')
    assert tasks_screen.family is None
    assert tasks_screen.tasks == []


@inapp_purchase
@override_settings(
    INAPP_PURCHASES=OrderedDict([
        ("lifetime_premium", {
            "icon": "atlas://data/atlas/purchases/lifetime_premium",
            "unlocks_tasks": ["division_calculation", "percents_calculation", "multiplication_calculation"],
            "type": "inapp"
        }),
        ("analytics_arena_pack", {
            "icon": "atlas://data/atlas/purchases/lifetime_premium",
            "unlocks_tasks": ["division_calculation", "percents_calculation", "multiplication_calculation"],
            "type": "inapp"
        }),
        ("time_arena_pack", {
            "icon": "atlas://data/atlas/purchases/lifetime_premium",
            "unlocks_tasks": ["division_calculation", "percents_calculation", "multiplication_calculation"],
            "type": "inapp"
        }),
        ("clash_arena_pack", {
            "icon": "atlas://data/atlas/purchases/lifetime_premium",
            "unlocks_tasks": ["division_calculation", "percents_calculation", "multiplication_calculation"],
            "type": "inapp"
        })
    ]), )
def test_purchase_try_now_after_bought(root_manager, detail_screen):
    import settings

    control.press(detail_screen.buy_button)
    control.press(detail_screen.buy_button)
    assert root_manager.current == 'tasks'
    tasks_screen = root_manager.get_screen('tasks')
    assert tasks_screen.family is None
    unlocked_tasks = settings.INAPP_PURCHASES[detail_screen.item_id]['unlocks_tasks']
    assert tasks_screen.tasks == unlocked_tasks


def test_internet_problems(billing_no_connection, screen):
    from screens.purchases.content import InternetProblemsScreen

    control.enter(screen)
    assert isinstance(screen.container.children[0], InternetProblemsScreen)
