import json
from kivy.logger import Logger

from jnius import JavaException
from jnius import autoclass, PythonJavaClass, java_method

import settings
from billing.abstract import AbstractBillingService, BillingException


class ServiceConnection(PythonJavaClass):
    __javainterfaces__ = ['android.content.ServiceConnection']
    __javacontext__ = 'app'

    def __init__(self, *args, **kwargs):
        super(ServiceConnection, self).__init__(*args, **kwargs)
        self.service = None
        self.bind_callback = None

    def register_bind_callback(self, callback):
        from kivy.clock import Clock

        self.bind_callback = Clock.create_trigger(callback)

    @java_method('(Landroid/content/ComponentName;)V')
    def onServiceDisconnected(self, name):
        Logger.info("Android billing: service disconnected")
        self.service = None

    @java_method('(Landroid/content/ComponentName;Landroid/os/IBinder;)V')
    def onServiceConnected(self, name, service):
        Logger.info("Android Billing: service connected")
        Stub = autoclass("com.android.vending.billing.IInAppBillingService$Stub")
        self.service = Stub.asInterface(service)
        if self.bind_callback:
            Logger.info("Android Billing: invoke connection callback %s" % self.bind_callback)
            self.bind_callback()
            self.bind_callback = None

    @java_method('()I')
    def hashCode(self):
        # hack because of the python and c long type error
        return (id(self) % 2147483647)

    @java_method('()Ljava/lang/String;', name='hashCode')
    def hashCode_(self):
        return '{}'.format(id(self))

    @java_method('()Ljava/lang/String;')
    def toString(self):
        return '{}'.format(self)

    @java_method('(Ljava/lang/Object;)Z')
    def equals(self, obj):
        return obj.hashCode() == self.hashCode()


class AndroidBillingService(AbstractBillingService):
    RC_BILLING = 1101
    RESULT_OK = -1

    def __init__(self):
        super(AndroidBillingService, self).__init__()
        from jnius import JavaException

        try:
            self.service_connection = ServiceConnection()
        except JavaException:
            Logger.error("Android Billing: can't instantiate ServiceConnection java class")
            self.service_connection = None
        self.python_activity = None
        self.developer_payload = None

    def bind(self, callback=None):
        if not self.service_connection:
            Logger.error("Android Billing: service connection is null, can't bind")
            return
        super(AndroidBillingService, self).bind()
        Intent = autoclass('android.content.Intent')
        Context = autoclass('android.content.Context')
        service_intent = Intent("com.android.vending.billing.InAppBillingService.BIND")
        service_intent.setPackage("com.android.vending")

        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        self.python_activity = PythonActivity.mActivity
        self.service_connection.register_bind_callback(callback)
        self.python_activity.bindService(service_intent,
                                         self.service_connection,
                                         Context.BIND_AUTO_CREATE)

    def unbind(self):
        if not self.service_connection:
            Logger.error("Android Billing: service connection is null, can't bind")
            return

        super(AndroidBillingService, self).unbind()
        if self.service_connection.service is not None:
            from jnius import JavaException

            try:
                self.python_activity.unbindService(self.service_connection)
            except JavaException:
                Logger.error("Android Billing: can't unbind service, pass...")
            self.service_connection.service = None

    def on_activity_result(self, request_code, result_code, data):
        import json

        Logger.info("Android Billing: back from resolution. "
                    "Request code: %s, result code: %s, data: %s" % (request_code, result_code, data))

        if request_code == self.RC_BILLING:
            # response_code = data.getIntExtra("RESPONSE_CODE", 0)
            purchase_data = data.getStringExtra("INAPP_PURCHASE_DATA")

            Logger.info("Android Billing: response code %s" % result_code)
            # data_signature = data.getStringExtra("INAPP_DATA_SIGNATURE")

            if result_code == self.RESULT_OK:
                try:
                    if purchase_data:
                        purchase = json.loads(purchase_data)
                    else:
                        purchase = None

                    if not purchase['developerPayload'] == self.developer_payload:
                        Logger.warning("Android Billing: wrong developer payload. Wait %s, got %s" %
                                       (self.developer_payload, purchase['developerPayload']))
                        return
                    else:
                        Logger.info("Android Billing: developer payload verified")
                        self.developer_payload = None
                    if purchase:
                        Logger.info("Android Billing: successful purchase, callbacks...")
                        from kivy.clock import Clock
                        from kivy.properties import partial

                        Clock.create_trigger(partial(self.billing_callback, purchase))()
                except ValueError:
                    Logger.error("Can't parse purchase json data: %s" % purchase_data)

    def buy(self, sku, callbacks=None):
        import uuid

        Intent = autoclass('android.content.Intent')
        try:
            super(AndroidBillingService, self).buy(sku, callbacks)
        except BillingException:
            return

        if not self.service:
            return
        self.developer_payload = str(uuid.uuid4())
        buy_intent_bundle = self.service.getBuyIntent(3,
                                                      self.python_activity.getPackageName(),
                                                      sku, settings.INAPP_PURCHASES[sku]['type'],
                                                      self.developer_payload)
        response = buy_intent_bundle.getInt("BILLING_RESPONSE_RESULT_OK")
        if response == 0:
            Logger.info("Android Billing: buy response OK")
            pending_intent = buy_intent_bundle.getParcelable("BUY_INTENT")
            if not pending_intent:
                return
            from jnius import cast

            pending_intent = cast('android.app.PendingIntent', pending_intent)
            # noinspection PyUnresolvedReferences
            from android import activity

            activity.bind(on_activity_result=self.on_activity_result)
            sender = pending_intent.getIntentSender()
            self.python_activity.startIntentSenderForResult(sender,
                                                            self.RC_BILLING,
                                                            Intent(), 0, 0, 0)
            if self._purchased_items:
                self._purchased_items = []
        else:
            Logger.warning("Android Billing: buy attempt code is not OK, but %s" % response)

    def get_purchased_items(self):
        super(AndroidBillingService, self).get_purchased_items()

        if not self.service:
            return []

        if self._purchased_items:
            Logger.info("Android Billing: return cached purchased items")
            return self._purchased_items

        from jnius import JavaException

        try:
            owned_inapp_items = self.service.getPurchases(3, self.python_activity.getPackageName(), "inapp", None)
        except JavaException:
            return []

        response = owned_inapp_items.getInt("RESPONSE_CODE")
        if response == 0:
            owned_skus = owned_inapp_items.getStringArrayList("INAPP_PURCHASE_ITEM_LIST").toArray()
            # purchased_data = owned_items.getStringArrayList("INAPP_PURCHASE_DATA_LIST").toArray()
            # signatures = owned_items.getStringArrayList("INAPP_DATA_SIGNATURE").toArray()
            # continuation_token = owned_items.getString("INAPP_CONTINUATION_TOKEN")
        else:
            Logger.warning("Android Billing: get available inapp details code is not OK, but %s" % response)
            return []

        try:
            owned_subs = self.service.getPurchases(3, self.python_activity.getPackageName(), "subs", None)
        except JavaException:
            return []

        response = owned_subs.getInt("RESPONSE_CODE")
        if response == 0:
            owned_subs_skus = owned_subs.getStringArrayList("INAPP_PURCHASE_ITEM_LIST").toArray()
            Logger.info("Android Billing: owned subs skus: %s" % owned_subs_skus)
            owned_skus += owned_subs_skus
        else:
            Logger.warning("Android Billing: get available subs details code is not OK, but %s" % response)
            return []

        if not self._purchased_items:
            self._purchased_items = owned_skus
        Logger.info("Android Billing: owned skus: %s" % owned_skus)
        return owned_skus

    def check_test_sku(self):
        if settings.DEVELOPMENT_VERSION:
            purchased_items = self.get_purchased_items()
            Logger.info("Android Billing: purchased items: %s" % purchased_items)
            if 'android.test.purchased' in purchased_items:
                Logger.info("Android Billing: android.test.purchased found, consume...")
                package_name = self.python_activity.getPackageName()
                purchase_token = "inapp:" + package_name + ":android.test.purchased"
                response = self.service.consumePurchase(3, package_name, purchase_token)
                if response == 0:
                    Logger.info("Android Billing: successfully purchased test sku")
                else:
                    Logger.warning("Android Billing: purchase test sku NOT OK, response: %s" % response)

    def check_inapp(self, query):
        try:
            inapp_details = self.service.getSkuDetails(3, self.python_activity.getPackageName(), "inapp", query)
        except JavaException:
            return []
        response = inapp_details.getInt("RESPONSE_CODE")
        if response == 0:
            response_list = inapp_details.getStringArrayList("DETAILS_LIST").toArray()
            return [json.loads(d) for d in response_list]
        else:
            Logger.warning("Android Billing: get available sku details code is not OK, but %s" % response)
        return []

    def check_subscriptions(self, query):
        try:
            subs_details = self.service.getSkuDetails(3, self.python_activity.getPackageName(), "subs", query)
        except JavaException:
            return []
        response = subs_details.getInt("RESPONSE_CODE")
        if response == 0:
            response_list = subs_details.getStringArrayList("DETAILS_LIST").toArray()
            subs_result = [json.loads(d) for d in response_list]
            Logger.info("Android Billing: available subs OK: %s" % [r['productId'] for r in subs_result])
            return subs_result
        else:
            Logger.warning("Android Billing: get available sku details code is not OK, but %s" % response)
        return []

    def get_available_items(self):

        super(AndroidBillingService, self).get_available_items()

        if not self.service:
            return []

        if self._available_items:
            Logger.info("Android Billing: return cached available items")
            return self._available_items

        ArrayList = autoclass('java.util.ArrayList')
        sku_list = ArrayList()

        for key in settings.INAPP_PURCHASES:
            sku_list.add(key)

        self.check_test_sku()

        Bundle = autoclass('android.os.Bundle')
        query = Bundle()
        query.putStringArrayList("ITEM_ID_LIST", sku_list)

        result = self.check_inapp(query) + self.check_subscriptions(query)
        Logger.info("Android Billing: available items OK: %s" % [r['productId'] for r in result])

        if not self._available_items:
            self._available_items = result
        return result

    @property
    def service(self):
        if not self.service_connection:
            Logger.error("Android Billing: service connection is null, can't bind")
            return

        return self.service_connection.service
