from kivy import Logger


class AbstractBillingService(object):
    def __init__(self, *args, **kwargs):
        self.callbacks = None
        self._purchased_items = []
        self._available_items = []

    def billing_callback(self, purchase, *largs):

        if not purchase:
            return

        Logger.info("Billing: callback, sku: %s, largs: %s" % (purchase['productId'], largs))
        if self.callbacks:
            for callback in self.callbacks:
                callback(purchase, *largs)

    def bind(self, callback=None):
        Logger.info("Billing: bind to billing service")

    def unbind(self):
        Logger.info("Billing: unbind from billing service")

    def buy(self, sku, callbacks=None):
        Logger.info("Billing: buy attempt %s" % sku)
        self.callbacks = callbacks
        if sku in self.get_purchased_items():
            Logger.error("Billing: attempt to buy already bought product...")
            raise AlreadyBoughtException()

    def get_purchased_items(self):
        pass

    def get_available_items(self):
        Logger.info("Billing: querying available items")
        return []

    def get_item_info(self, item_id):
        for item in self.get_available_items():
            if item['productId'] == item_id:
                return item

    def get_available_skus(self):
        return [item['productId'] for item in self.get_available_items()]


class BillingException(Exception):
    pass


class AlreadyBoughtException(BillingException):
    pass
