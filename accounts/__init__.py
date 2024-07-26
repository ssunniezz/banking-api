# Let's use my own conversion logic for convenience
from decimal import Decimal

USD_TO_THB_RATE = 30
THB_TO_USD_RATE = 0.033


def convert(currency: str, target_currency: str, amount: Decimal) -> Decimal:
    if currency == 'USD' and target_currency == 'THB':
        return amount * USD_TO_THB_RATE

    if currency == 'THB' and target_currency == 'USD':
        return amount * Decimal(THB_TO_USD_RATE)

    return amount
