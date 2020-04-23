from django_filters import rest_framework as filters

from accounts.models import Transaction


class TransactionFilter(filters.FilterSet):
    o = filters.OrderingFilter(
        fields=('timestamp', 'amount')
    )

    class Meta:
        model = Transaction
        exclude = ()
        fields = (
            'from_account',
            'to_account',
            'timestamp',
            'amount',
            'status',
        )
