from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, TransactionViewSet, CustomAccountViewSet

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'custom_accounts', CustomAccountViewSet, basename='custom_account')

urlpatterns = [
    path('', include(router.urls)),
]
