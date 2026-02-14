"""
MercadoLibre-specific price parsing.

Extracted from domain/value_objects.py Money.from_mercadolibre_string()
to decouple the domain from MercadoLibre specifics.
"""
from __future__ import annotations

from domain.enums import Currency
from domain.value_objects import Money


def parse_mercadolibre_price(price_str: str) -> Money | None:
    """Parse a MercadoLibre price string into a Money object.

    Args:
        price_str: Price string like "U$S 15.000" or "$ 150.000".

    Returns:
        Money instance or None if parsing fails.
    """
    if not price_str or not isinstance(price_str, str):
        return None

    price_str = price_str.strip()

    if "U$S" in price_str:
        currency = Currency.USD
        number_str = price_str.replace("U$S", "")
    elif "$" in price_str:
        currency = Currency.ARS
        number_str = price_str.replace("$", "")
    else:
        return None

    number_str = number_str.replace(".", "").strip()
    if not number_str:
        return None

    try:
        amount = float(number_str)
    except ValueError:
        return None

    return Money(amount=amount, currency=currency)
