from decimal import Decimal

from django.conf import settings
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.api.filters import TransactionFilter
from accounts.api.serializers import CustomerAccountSerializer, TransactionSerializer
from accounts.models import CustomerAccount, Transaction
from accounts.tasks import delay_transaction_commit


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post']
    filterset_class = TransactionFilter
    filter_backends = (filters.DjangoFilterBackend,)

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.from_account.owner == instance.to_account.owner:
            instance.fee = Decimal(0)
        else:
            instance.fee = instance.amount * settings.COMISSION
        instance.save()
        delay_transaction_commit(instance)

    def get_queryset(self):
        if self.request.user.is_staff:
            return Transaction.objects.all()
        else:
            return Transaction.objects.filter(
                from_account__in=CustomerAccount.objects.filter(
                    owner=self.request.user
                )
            )


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerAccountSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post']
    filter_backends = ()

    def get_queryset(self):
        if self.request.user.is_staff:
            return CustomerAccount.objects.all()
        else:
            return CustomerAccount.objects.filter(owner=self.request.user)
