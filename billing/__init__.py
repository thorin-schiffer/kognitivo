from kivy.utils import platform

import settings

if platform == 'android' and not settings.PROFILE:
    from billing.android_billing import AndroidBillingService

    BillingService = AndroidBillingService
else:
    from billing.dummy import DummyBillingService

    BillingService = DummyBillingService
