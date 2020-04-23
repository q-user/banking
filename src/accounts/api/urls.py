from django.urls import path
from rest_framework.routers import DefaultRouter

from accounts.api.views import AccountViewSet, TransactionViewSet

app_name = 'accounts'

account_router = DefaultRouter()
account_router.register(r'accounts', AccountViewSet, basename='account')
account_router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = []
urlpatterns += account_router.urls
