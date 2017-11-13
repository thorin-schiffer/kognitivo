import pytest
import settings

inapp_purchase = pytest.mark.skipif(not settings.INAPP_PURCHASES, reason="No in app purchases")
