from django.urls import path, include
from rest_framework.routers import DefaultRouter
from itemcode.views import ItemCodeViewSet

router = DefaultRouter()
router.register('items-code', ItemCodeViewSet, basename='items-code')

urlpatterns = [
    path('', include(router.urls)),
    ]
