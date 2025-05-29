from rest_framework.routers import DefaultRouter
from .views import MarisInputViewSet

router = DefaultRouter()
router.register(r'maris', MarisInputViewSet, basename='maris')

urlpatterns = router.urls
