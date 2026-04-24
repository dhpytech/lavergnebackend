from django.urls import path
from .apis.maris_api import MarisDashboardAPI
from .apis.audit_api import MarisAuditAPI
from .apis.bagging_api import BaggingDashboardAPI


urlpatterns = [
    path("maris/", MarisDashboardAPI.as_view(), name="maris-dashboard"),
    path('maris/audit/', MarisAuditAPI.as_view(), name='maris-audit'),
    # path("dashboard/metal/", MetalDashboardAPI.as_view()),
    path('bagging/', BaggingDashboardAPI.as_view() , name='bagging-dashboard'),
]
