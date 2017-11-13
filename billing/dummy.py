from kivy import Logger

import settings
from billing.abstract import AbstractBillingService


class DummyBillingService(AbstractBillingService):
    def __init__(self, *args, **kwargs):
        super(DummyBillingService, self).__init__(*args, **kwargs)

    def bind(self, callback=None):
        super(DummyBillingService, self).bind(callback)
        Logger.info("Dummy Billing: invoke connection callback %s" % callback)
        from kivy.clock import Clock
        if callback:
            Clock.schedule_once(callback, timeout=1)

    def buy(self, sku, callbacks=None):
        super(DummyBillingService, self).buy(sku, callbacks)

        self._purchased_items.append(sku)

        dummy_purchase = {
            "orderId": "12999763169054705758.1371079406387615",
            "packageName": "org.kognitivo.kognitivo",
            "productId": sku,
            "purchaseTime": 1345678900000,
            "purchaseState": 0,
            "developerPayload": "bGoa+V7g/yqDXvKRqq+JTFn4uQZbPiQJo4pf9RzJ",
            "purchaseToken": "opaque-token-up-to-1000-characters"
        }

        self.billing_callback(dummy_purchase, self._purchased_items)

    def get_purchased_items(self):
        return self._purchased_items

    def get_available_items(self):
        super(DummyBillingService, self).get_available_items()
        if self._available_items:
            Logger.info("Dummy Billing: return cached available items")
            return self._available_items
        result = [
            {
                "title": "%s (KOGNITIVO Brain Trainer)" % sku.replace("_", " ").replace(".", " ").capitalize(),
                "price": u'\u20ac0.88',
                "type": "inapp",
                "description": "It tastes so good! Thank you!",
                "price_amount_micros": 1130000,
                "price_currency_code": "EUR",
                "productId": sku
            } for sku in settings.INAPP_PURCHASES.keys()
        ]
        if not self._available_items:
            self._available_items = result
        return self._available_items
