from django.urls import path,include
from rest_framework.routers import DefaultRouter
from dlnc_case.views import DlncCaseViewSet


router = DefaultRouter()
router.register('dlnc_case', DlncCaseViewSet, basename='dlnc_case')

urlpatterns = [
    path('', include(router.urls)),
]