from django.urls import path,include
from rest_framework.routers import DefaultRouter
from problems.views import ProblemViewSet

router = DefaultRouter()
router.register('problems', ProblemViewSet, basename='problems')
urlpatterns = [
    path('', include(router.urls)),
]