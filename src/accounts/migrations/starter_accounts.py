# Generated by Django 3.0.5 on 2020-04-22 10:11
from decimal import Decimal

from django.db import migrations, IntegrityError

from accounts.models import AccountCurrencyChoices


def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    BankAccount = apps.get_model('accounts', 'BankAccount')
    Account = apps.get_model('accounts', 'Account')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ba_ct = ContentType.objects.get_for_model(BankAccount)

    for currency in AccountCurrencyChoices.values:
        try:
            ba = BankAccount.objects.create(
                currency=currency, balance=Decimal(100000)
            )
            Account.objects.filter(
                id=ba.account_ptr_id
            ).update(polymorphic_ctype_id=ba_ct)
        except IntegrityError as e:
            pass


def reverse_func(apps, schema_editor):
    BankAccount = apps.get_model('accounts', 'BankAccount')
    db_alias = schema_editor.connection.alias

    BankAccount.objects.using(db_alias).all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func)
    ]
