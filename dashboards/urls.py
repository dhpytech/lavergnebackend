from django.urls import path
from dashboards.apis.maris_api import MarisDashboardAPI

urlpatterns = [
    path("maris/", MarisDashboardAPI.as_view(), name="maris-dashboard"),
    # path("dashboard/metal/", MetalDashboardAPI.as_view()),
    # path("dashboard/bagging/", BaggingDashboardAPI.as_view()),
]
