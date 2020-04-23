from rest_framework import serializers
from accounts.models import CustomerAccount, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    timestamp = serializers.ReadOnlyField()
    fee = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    description = serializers.ReadOnlyField()
    new_from_balance = serializers.ReadOnlyField()
    new_to_balance = serializers.ReadOnlyField()
    status = serializers.CharField(source='get_status_display', read_only=True)
    error_msg = serializers.ReadOnlyField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.fields['from_account'].queryset = CustomerAccount.objects.filter(
            owner=self.context['request'].user
        )
        self.fields.fields['to_account'].queryset = CustomerAccount.objects.all()

    class Meta:
        model = Transaction
        exclude = ()

    def validate(self, attrs):
        super().validate(attrs)

        from_account = attrs['from_account']
        to_account = attrs['to_account']

        errors = {}

        if from_account.owner != self.context['request'].user:
            errors.update({
                'from_account': ['Пожалуйста, укажите корректное значение счёта отправителя.']
            })

        if from_account == to_account:
            errors.update({
                'to_account_id': ['Пожалуйста, выберите другой счёт для перевода.']
            })

        if from_account.currency != to_account.currency:
            errors.update({
                'to_account_id': ['Пожалуйста, выберите счёт получатель в той же валюте.']
            })

        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class CustomerAccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = CustomerAccount
        exclude = ('timestamp', 'polymorphic_ctype',)

    def create(self, validated_data):
        validated_data.update({
            'owner': self.context['request'].user
        })
        return super().create(validated_data)
