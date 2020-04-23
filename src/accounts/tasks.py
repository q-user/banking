from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone

from accounts.models import Transaction


def delay_transaction_commit(transaction):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        commit_transaction_task,
        'date',
        run_date=timezone.now() + timedelta(microseconds=1000),
        args=[transaction.id],
        max_instances=1
    )
    scheduler.start()


def commit_transaction_task(transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    transaction.commit()
