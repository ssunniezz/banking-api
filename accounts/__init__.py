# Let's use my own conversion logic for convenience
from decimal import Decimal


def convert(currency: str, target_currency: str, amount: Decimal) -> Decimal:
    if currency == target_currency:
        return amount

    if currency == 'USD':
        return amount * 30

    if currency == 'THB':
        return amount * Decimal(0.033)
