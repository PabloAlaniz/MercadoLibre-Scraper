"""
Immutable value objects for the domain layer.

Retailer-specific parsing (e.g. MercadoLibre price strings)
belongs in the respective scraper package.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from domain.enums import Currency


@dataclass(frozen=True)
class Money:
    """Represents a monetary amount with currency."""
    amount: float
    currency: Currency

    def convert_to(self, target_currency: Currency, rate: float) -> Money:
        """Convert to another currency using the given exchange rate.

        The rate is always USD->ARS (how many ARS per 1 USD).
        """
        if self.currency == target_currency:
            return self

        if self.currency == Currency.USD and target_currency == Currency.ARS:
            return Money(amount=self.amount * rate, currency=Currency.ARS)
        elif self.currency == Currency.ARS and target_currency == Currency.USD:
            return Money(amount=round(self.amount / rate), currency=Currency.USD)

        return self


@dataclass(frozen=True)
class Kilometers:
    """Represents a distance in kilometers."""
    value: int

    @classmethod
    def from_string(cls, km_str: str) -> Kilometers | None:
        """Parse a km string like "50.000 km" into a Kilometers object."""
        if not km_str or not isinstance(km_str, str):
            return None

        cleaned = km_str.replace(' km', '').replace('km', '').replace('.', '').strip()
        if not cleaned:
            return None

        try:
            return cls(value=int(cleaned))
        except ValueError:
            return None


@dataclass(frozen=True)
class SquareMeters:
    """Represents an area in square meters."""
    value: float

    @classmethod
    def from_string(cls, m2_str: str) -> SquareMeters | None:
        """Parse an m2 string like "150 m² totales" into a SquareMeters object."""
        if not m2_str or not isinstance(m2_str, str):
            return None

        match = re.search(r'([\d.,]+)\s*m²', m2_str)
        if not match:
            return None

        number_str = match.group(1).replace('.', '').replace(',', '.')
        try:
            return cls(value=float(number_str))
        except ValueError:
            return None
