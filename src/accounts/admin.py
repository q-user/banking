from allauth.account.models import EmailAddress
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

from accounts.models import Account, Transaction


class AccountAdmin(admin.ModelAdmin):
    list_display = ('to_str', 'balance')

    def to_str(self, obj):
        return str(obj)


class TransactionAdmin(admin.ModelAdmin):
    pass


admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.unregister(Group)
admin.site.unregister(EmailAddress)
admin.site.unregister(Site)
