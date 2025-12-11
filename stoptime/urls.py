from django.urls import path, include
from rest_framework.routers import DefaultRouter
from stoptime.views import StopTimeViewSet

router = DefaultRouter()
router.register('stop-time', StopTimeViewSet, basename='stop-time')

urlpatterns = [
    path('', include(router.urls)),
    ]