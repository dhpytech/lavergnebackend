from django.urls import path
from .apis.maris_api import MarisDashboardAPI
from .apis.audit_api import MarisAuditAPI
from .apis.bagging_api import BaggingDashboardAPI
from .apis.metal_api import MetalDashboardAPI
from .apis.maris_monthly import MarisMonthlyAnalyticsView


urlpatterns = [
    path("maris/", MarisDashboardAPI.as_view(), name="maris-dashboard"),
    path('maris/audit/', MarisAuditAPI.as_view(), name='maris-audit'),
    path('bagging/', BaggingDashboardAPI.as_view(), name='bagging-dashboard'),
    path('metal/', MetalDashboardAPI.as_view(), name='metal-dashboard'),
    path('monthly-maris', MarisMonthlyAnalyticsView.as_view(), name='maris-monthly-analytics'),
]
