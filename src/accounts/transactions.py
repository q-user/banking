class InsufficientFundsException(Exception):
    pass


def transfer(from_account, to_account, amount, comission=0):
    total = amount + comission
    if from_account.balance - total < 0:
        raise InsufficientFundsException(
            'Недостаточно средств на балансе.'
        )
